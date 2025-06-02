from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EnterpriseBase(BaseModel):
    name: str
    industry: str
    inn: str
    short_name: str
    is_active: bool = True

class EnterpriseCreate(EnterpriseBase):
    pass

class EnterpriseOut(EnterpriseBase):
    id: int
    create_at: datetime
    class Config:
        model_config = ConfigDict(from_attributes=True)