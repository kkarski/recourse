import pytest
import asyncio
import os
import tempfile
import json
from uuid import uuid4
from datetime import datetime

from recourse.story.workflow import StorySyncWorkflow, run_story_sync_workflow
from recourse.story.event import StoryEvent, ActionType, EntityType
from recourse.model import Story, Description


@pytest.fixture
def sample_story():
    """Create a story with content from evaluate_story_against_criteria.md"""
    story_content = """
    The "platform" must be able to evaluate a product specification or story against 
    a template and success critiera and provide a list of suggested improvements to the specification
    in order comply with both the template and success criteria. 

    The user of the "platform" may provide their answers in the form of comments to earlier questions or suggestions. 
    When instructed, the "platform" should take the answers and comments provided by the user and update the specification
    per the template and success criteria with the user's provided information.
    """
    
    return Story(
        id=uuid4(),
        title="Platform Story Evaluation Feature",
        content=[Description(
            text=story_content.strip(),
            version=1,
            updated_by="test_user"
        )],
        updated_by="test_user"
    )


@pytest.fixture
def story_event(sample_story):
    """Create a StoryEvent for the sample story"""
    return StoryEvent(
        entity_id=str(sample_story.id),
        entity_type=EntityType.story,
        action_type=ActionType.created,
        timestamp=datetime.now(),
        user_id="test_user"
    )


@pytest.fixture
def jira_credentials():
    """Real JIRA credentials from environment variables"""
    return {
        "email": os.getenv("JIRA_EMAIL"),
        "api_token": os.getenv("JIRA_API_TOKEN"),
        "server_url": os.getenv("JIRA_SERVER_URL")
    }


@pytest.fixture
def temp_context_dir():
    """Create temporary directory for context files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_story_sync_workflow_integration(
    story_event, 
    jira_credentials, 
    sample_story,
    temp_context_dir
):
    """Integration test for StorySyncWorkflow with real JIRA and Gemini API calls"""
    
    # Skip test if required environment variables are not set
    if not all([
        jira_credentials["email"],
        jira_credentials["api_token"], 
        jira_credentials["server_url"],
        os.getenv("GEMINI_API_KEY")
    ]):
        pytest.skip("Required environment variables not set: JIRA_EMAIL, JIRA_API_TOKEN, JIRA_SERVER_URL, GEMINI_API_KEY")
    
    # Run the workflow
    result = await run_story_sync_workflow(
        ev=story_event,
        jira_project="TEST",
        story_id=str(sample_story.id),
        credentials=jira_credentials
    )
    
    # Validate results
    assert result is not None
    assert hasattr(result, 'story')
    assert hasattr(result, 'feedback')
    assert len(result.feedback) > 0
    
    # Validate story structure
    assert result.story.id is not None
    assert result.story.title is not None
    assert result.story.updated_by is not None
    
    # Validate feedback content contains JTBD evaluation
    feedback_text = result.feedback[0].text
    assert len(feedback_text) > 0
    
    # Check that feedback addresses key JTBD criteria
    feedback_lower = feedback_text.lower()
    jtbd_keywords = [
        "circumstance", "progress", "emotional", "functional", 
        "social", "forces", "anxiety", "customer"
    ]
    
    # At least some JTBD concepts should be mentioned in feedback
    mentioned_concepts = sum(1 for keyword in jtbd_keywords if keyword in feedback_lower)
    assert mentioned_concepts >= 3, f"Feedback should mention JTBD concepts, found: {mentioned_concepts}"
    
    # Validate context file was created
    ctx_file = f"workflow_ctx_TEST_{sample_story.id}.json"
    assert os.path.exists(ctx_file)
    
    # Validate context file contains expected data
    with open(ctx_file, 'r') as f:
        ctx_data = json.load(f)
    
    assert 'store' in ctx_data
    assert 'state' in ctx_data['store']
    
    state = ctx_data['store']['state']
    assert 'story_feedbacks' in state
    assert str(sample_story.id) in state['story_feedbacks']
    
    stored_feedback = state['story_feedbacks'][str(sample_story.id)]
    assert 'story' in stored_feedback
    assert 'feedback' in stored_feedback
    assert stored_feedback['updated_by'] == 'gemini-pro'


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_context_persistence(
    story_event,
    jira_credentials, 
    sample_story,
    temp_context_dir
):
    """Test that workflow context is properly persisted and reused"""
    
    # Skip test if required environment variables are not set
    if not all([
        jira_credentials["email"],
        jira_credentials["api_token"], 
        jira_credentials["server_url"],
        os.getenv("GEMINI_API_KEY")
    ]):
        pytest.skip("Required environment variables not set")
    
    # Run workflow first time
    result1 = await run_story_sync_workflow(
        ev=story_event,
        jira_project="TEST",
        story_id=str(sample_story.id),
        credentials=jira_credentials
    )
    
    # Run workflow second time - should reuse cached feedback
    result2 = await run_story_sync_workflow(
        ev=story_event,
        jira_project="TEST", 
        story_id=str(sample_story.id),
        credentials=jira_credentials
    )
    
    # Results should be identical (cached)
    assert result1.feedback[0].text == result2.feedback[0].text
    assert result1.feedback[0].updated_by == result2.feedback[0].updated_by
