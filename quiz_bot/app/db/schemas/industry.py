from pydantic import BaseModel, ConfigDict

class IndustryBase(BaseModel):
    name: str
    description: str

class IndustryCreate(IndustryBase):
    pass

class IndustryOut(IndustryBase):
    id: int
    class Config:
        model_config = ConfigDict(from_attributes=True)