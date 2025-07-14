import uuid
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class Description(BaseModel):
  text: str
  version: int
  updated_at: datetime = datetime.now()
  updated_by: str


class Comment(BaseModel):
  text: str
  updated_at: datetime = datetime.now()
  updated_by: str


class Story(BaseModel):
  content: List[Description] = list()
  comments: List[Comment] = list()
  id: UUID = uuid.uuid4()
  title: str = 'Story'
  updated_at: datetime = datetime.now()
  updated_by: str

  # Context object for JIRA credentials


class Context(BaseModel):
  email: str
  api_token: str
  server_url: str


class Feedback(BaseModel):
  text: str
  index: int


class StoryFeedback(BaseModel):
  story: Story
  feedback: List[Feedback] = list()
  updated_at: datetime = datetime.now()
  updated_by: str
