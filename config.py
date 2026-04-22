from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    db_path: str = "./Company.db"
    gmail_credentials_path: str
    gmail_token_path: str
    groq_api_key :str
    from_email: str = "me"
    lead_services: str = "xyz, abc, lmnop"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

