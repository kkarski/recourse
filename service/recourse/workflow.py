import json
import os
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from llama_index.core.workflow import (
    Workflow,
    step,
    Context as AgentContext,
    Event as LlamaEvent,
    StopEvent,
)

from recourse.schemas import Feedback, DocumentUpdatedEvent, Author


class FeedbackWorkflow(Workflow):
    def __init__(self, feedback_file_path: str = "feedback.json", **kwargs):
        super().__init__(**kwargs)
        self.feedback_file_path = feedback_file_path

    @step
    async def write_feedback_to_file(
        self, ctx: AgentContext, ev: LlamaEvent
    ) -> StopEvent:
        """
        Writes all feedback stored in the workflow context to a feedback file
        by serializing all feedback objects into JSON using Pydantic.
        """
        state = await ctx.store.get("state") or {}
        
        # Collect all feedback objects from state
        all_feedback: List[Feedback] = []
        
        # Check for feedbacks stored in various possible locations
        # Look for 'feedbacks' key (list of feedback dicts)
        if "feedbacks" in state:
            feedback_data_list = state["feedbacks"]
            for feedback_data in feedback_data_list:
                if isinstance(feedback_data, dict):
                    try:
                        feedback = Feedback(**feedback_data)
                        all_feedback.append(feedback)
                    except Exception as e:
                        # Skip invalid feedback entries
                        continue
        
        # Look for 'story_feedbacks' key (dict of story_id -> feedback dict)
        if "story_feedbacks" in state:
            story_feedbacks = state["story_feedbacks"]
            for story_id, feedback_data in story_feedbacks.items():
                if isinstance(feedback_data, dict):
                    # Check if feedback_data contains a list of feedbacks
                    if "feedback" in feedback_data and isinstance(feedback_data["feedback"], list):
                        for fb in feedback_data["feedback"]:
                            if isinstance(fb, dict):
                                try:
                                    feedback = Feedback(**fb)
                                    all_feedback.append(feedback)
                                except Exception as e:
                                    continue
                    else:
                        # Try to parse as a single Feedback object
                        try:
                            feedback = Feedback(**feedback_data)
                            all_feedback.append(feedback)
                        except Exception as e:
                            continue
        
        # Serialize all feedback objects to JSON using Pydantic
        feedback_json_list = []
        for feedback in all_feedback:
            feedback_json = feedback.model_dump_json()
            feedback_json_list.append(json.loads(feedback_json))
        
        # Write to file
        os.makedirs(os.path.dirname(self.feedback_file_path) or ".", exist_ok=True)
        with open(self.feedback_file_path, "w") as f:
            json.dump(feedback_json_list, f, indent=2, default=str)
        
        return StopEvent(result={"feedback_count": len(all_feedback), "file_path": self.feedback_file_path})


# Load product manager prompt from file (at module load)
PRODUCT_MANAGER_PROMPT_PATH = Path(__file__).parent / "prompt" / "product_manager.md"
if PRODUCT_MANAGER_PROMPT_PATH.exists():
    with open(PRODUCT_MANAGER_PROMPT_PATH, "r") as f:
        PRODUCT_MANAGER_PROMPT = f.read()
else:
    PRODUCT_MANAGER_PROMPT = "Evaluate the document content and provide feedback as a Product Manager."


class ProductManagerEvalWorkflow(Workflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @step
    async def evaluate_document(
        self, ctx: AgentContext, ev: DocumentUpdatedEvent
    ) -> StopEvent:
        """
        Product manager evaluation workflow step that:
        - Takes a DocumentUpdatedEvent
        - Reads the file content from file_url
        - Executes Gemini 3.0 Flash LLM with structured output
        - Uses product_manager.md as system prompt
        - Returns Feedback (Question or Recommendation)
        - Stores feedback to workflow context
        """
        from google import genai

        # Initialize Gemini client
        client = genai.Client()

        # Read file content from file_url
        file_url = ev.file_url
        parsed_url = urlparse(file_url)
        
        # Handle file:// URLs and local file paths
        if parsed_url.scheme == "file" or not parsed_url.scheme:
            # Local file path
            file_path = parsed_url.path if parsed_url.scheme == "file" else file_url
            if not os.path.isabs(file_path):
                # Relative path - resolve relative to current working directory
                file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        else:
            # Handle other URL schemes (http, https, etc.)
            import urllib.request
            with urllib.request.urlopen(file_url) as response:
                file_content = response.read().decode("utf-8")

        # Prepare the evaluation prompt
        evaluation_prompt = f"""{PRODUCT_MANAGER_PROMPT}

Document Content:
{file_content}

Please evaluate this document and provide feedback. The feedback should be either a Question or a Recommendation."""

        # Execute Gemini 3.0 Flash with structured output
        response = client.models.generate_content(
            model="gemini-3.0-flash-preview",
            contents=evaluation_prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": Feedback.model_json_schema(),
            },
        )

        # Parse the structured response into Feedback object
        feedback = Feedback.model_validate_json(response.text)
        
        # Update feedback with event metadata
        feedback.author = ev.author
        feedback.revision = ev.revision
        feedback.file_url = ev.file_url
        feedback.timestamp = ev.timestamp

        # Store feedback to workflow context
        state = await ctx.store.get("state") or {}
        if "feedbacks" not in state:
            state["feedbacks"] = []
        
        # Add feedback to the list
        state["feedbacks"].append(feedback.model_dump())
        await ctx.store.set("state", state)

        return StopEvent(result=feedback)

