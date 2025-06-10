from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RespondentBase(BaseModel):
    enterprise_id: int
    full_name: str
    position: str
    phone: str
    email: str
    consent: bool = False

class RespondentCreate(RespondentBase):
    pass

class RespondentUpdate(BaseModel):
    enterprise_id: int
    full_name: str
    position: str
    phone: str
    email: str

class RespondentOut(RespondentBase):
    id: int
    create_at: datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)