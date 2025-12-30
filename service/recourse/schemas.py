import uuid
from datetime import datetime
from enum import Enum
from typing import Literal, List, Optional

from llama_index.core.workflow import StartEvent
from pydantic import BaseModel, Field


class Author(str, Enum):
    Architect = "Architect"
    QA = "QA"
    QA_Engineer = "QA Engineer"
    Backend_Engineer = "Backend Engineer"
    Front_End_Engineer = "Front End Engineer"
    User = "User"
    VP_of_Engineering = "VP of Engineering"
    Product_Manager = "Product Manager"


class Comment(BaseModel):
    author: Author
    timestamp: datetime = Field(default_factory=datetime.now)
    text: str


class Feedback(BaseModel):
    type: Literal["Question", "Recommendation"]
    author: Author
    timestamp: datetime = Field(default_factory=datetime.now)
    id: uuid.UUID = uuid.uuid4()
    is_resolved: bool = False
    is_rejected: bool = False
    is_approved: bool = False
    comments: List[Comment] = []
    text: str
    revision: str

class ProposedDocumentUpdateEvent(BaseModel):
    author: Author
    timestamp: datetime = Field(default_factory=datetime.now)
    revision: str
    text: str


class DocumentUpdatedEvent(BaseModel):
    file_url: str
    author: Author
    timestamp: datetime = Field(default_factory=datetime.now)
    revision: str
    
class UserRequestStartEvent(StartEvent):
    author: Author.User
    timestamp: datetime = Field(default_factory=datetime.now)
    text: str
    file_urls: List[str]
    

