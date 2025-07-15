from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event as LlamaEvent,
    Context as AgentContext,  # Use LlamaIndex's Context
    JsonSerializer,
)
from pydantic import BaseModel
from recourse.story.event import CommentEvent, StoryEvent, ActionType
from recourse.model import Story, StoryFeedback, Feedback
from typing import Any
import uuid
import os
import json

# Load JTBD criteria from file (at module load)
with open("req/recourse/standards/story-criteria.v1.md", "r") as f:
    JTBD_CRITERIA = f.read()


# Custom event for when a story is fetched from JIRA
class StoryFetchedEvent(LlamaEvent):
    story: Story


# Custom event for when story feedback is ready
class StoryFeedbackEvent(LlamaEvent):
    story: Story
    feedback: StoryFeedback


class StorySyncWorkflow(Workflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @step
    async def on_event(self, ctx: AgentContext, ev: LlamaEvent) -> StoryFetchedEvent:
        if not isinstance(ev, (CommentEvent, StoryEvent)):
            raise ValueError("Unsupported event type")
        if ev.action_type not in [
            ActionType.created.value,
            ActionType.update.value,
            ActionType.delete.value,
        ]:
            raise ValueError("Unsupported action type")
        state = await ctx.store.get("state") or {}
        email = state.get("email")
        api_token = state.get("api_token")
        server_url = state.get("server_url")
        if not (email and api_token and server_url):
            raise ValueError("JIRA credentials not found in context state")
        from llama_index.readers.jira import JiraReader

        reader = JiraReader(email=email, api_token=api_token, server_url=server_url)
        documents = reader.load_data(query=f"id = {ev.entity_id}")
        if not documents:
            raise ValueError(f"No story found for id {ev.entity_id}")
        doc = documents[0]
        story = Story(
            id=doc.extra_info.get("id", None),
            title=doc.extra_info.get("summary", "Story"),
            updated_by=doc.extra_info.get("updated_by", "jira"),
        )
        state["story"] = (
            story.model_dump() if hasattr(story, "model_dump") else story.dict()
        )
        await ctx.store.set("state", state)
        return StoryFetchedEvent(story=story)

    @step
    async def generate_story_feedback(
        self, ctx: AgentContext, ev: StoryFetchedEvent
    ) -> StoryFeedbackEvent:
        # Check for existing feedback in state
        state = await ctx.store.get("state") or {}
        feedbacks = state.get("story_feedbacks", {})
        story_id = str(ev.story.id)
        if story_id in feedbacks:
            feedback_data = feedbacks[story_id]
            feedback = StoryFeedback(**feedback_data)
        else:
            # Evaluate with Gemini Pro
            from llama_index.llms.google_genai import GoogleGenAI

            llm = GoogleGenAI(
                model="gemini-2.5-pro", api_key=os.getenv("GEMINI_API_KEY")
            )
            prompt = f"""{JTBD_CRITERIA}"""
            resp = llm.complete(prompt)
            feedback = StoryFeedback(
                story=ev.story,
                feedback=[Feedback(text=resp.text, index=0)],
                updated_at=ev.story.updated_at,
                updated_by="gemini-pro",
            )
            # Store feedback in state
            feedbacks[story_id] = feedback.model_dump()
            state["story_feedbacks"] = feedbacks
            await ctx.store.set("state", state)
        return StoryFeedbackEvent(story=ev.story, feedback=feedback)

    @step
    async def finish(self, ctx: AgentContext, ev: StoryFeedbackEvent) -> StopEvent:
        # Store the feedback in context state and finish
        state = await ctx.store.get("state") or {}
        feedbacks = state.get("story_feedbacks", {})
        story_id = str(ev.story.id)
        feedbacks[story_id] = ev.feedback.model_dump()

        state["story_feedbacks"] = feedbacks
        await ctx.store.set("state", state)
        return StopEvent(result=ev.feedback)


def get_context_file_path(jira_project: str, story_id: str) -> str:
    """Helper to get the context file path for a given project and story."""
    return f"workflow_ctx_{jira_project}_{story_id}.json"


async def run_story_sync_workflow(
    ev: LlamaEvent,
    jira_project: str,
    story_id: str,
    credentials: dict,
    workflow_kwargs: dict = None,
):
    """
    Entrypoint to run the StorySyncWorkflow with context serialization/deserialization.
    Args:
        ev: The event to trigger the workflow (CommentEvent or StoryEvent).
        jira_project: The JIRA project key.
        story_id: The story/entity id.
        credentials: Dict with 'email', 'api_token', 'server_url'.
        workflow_kwargs: Optional kwargs for StorySyncWorkflow.
    Returns:
        The workflow result.
    """
    workflow_kwargs = workflow_kwargs or {}
    workflow = StorySyncWorkflow(**workflow_kwargs)
    ctx_file = get_context_file_path(jira_project, story_id)
    serializer = JsonSerializer()

    # Try to load context from file
    if os.path.exists(ctx_file):
        with open(ctx_file, "r") as f:
            ctx_dict = json.load(f)
        ctx = AgentContext.from_dict(workflow, ctx_dict, serializer=serializer)
    else:
        ctx = AgentContext(workflow)
        # Set credentials in state
        await ctx.store.set("state", credentials)

    # Run the workflow
    result = await workflow.run(ev=ev, ctx=ctx)

    # Serialize context to file
    ctx_dict = ctx.to_dict(serializer=serializer)
    with open(ctx_file, "w") as f:
        json.dump(ctx_dict, f)

    return result
