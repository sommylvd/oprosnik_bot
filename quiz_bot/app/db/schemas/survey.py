from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SurveyBase(BaseModel):
    respondent_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    ip_address: str
    user_agent: str

class SurveyCreate(SurveyBase):
    pass

class SurveyOut(SurveyBase):
    id: int
    class Config:
        model_config = ConfigDict(from_attributes=True)