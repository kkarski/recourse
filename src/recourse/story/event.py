import uuid
from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel

from story.model import Comment


class Event(BaseModel):
  id: uuid.UUID = uuid.uuid4()
  metadata: Dict[str, Any] = {}


class EntityType(str, Enum):
  story = "recourse.story"
  comment = "comment"


class ActionType(str, Enum):
  created = "created"
  update = "updated"
  delete = "deleted"


class CommentEvent(Event):
  entity_type: str = EntityType.comment.value
  action_type: str = ActionType.created.value
  comment: Comment
  entity_id: str

class StoryEvent(Event):
  entity_type: str = EntityType.story.value
  action_type: str = ActionType.created.value

