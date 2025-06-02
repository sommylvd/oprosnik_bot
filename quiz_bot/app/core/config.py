from typing import Optional
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
   
    class Config:
        env_file = ".env"

    

config = Settings()