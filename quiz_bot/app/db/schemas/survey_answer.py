from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SurveyAnswerBase(BaseModel):
    survey_id: int
    question_id: int
    answer: dict

class SurveyAnswerCreate(SurveyAnswerBase):
    pass

class SurveyAnswerUpdate(BaseModel):
    answer: dict

class SurveyAnswerOut(SurveyAnswerBase):
    id: int
    created_at: datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)