from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class QuestionBase(BaseModel):
    number: int
    text: str
    answer_type: str

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    created_at: datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)