from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SoftwareCategoryBase(BaseModel):
    name: str
    description: str

class SoftwareCategoryCreate(SoftwareCategoryBase):
    pass

class SoftwareCategoryOut(SoftwareCategoryBase):
    id: int
    class Config:
        model_config = ConfigDict(from_attributes=True)