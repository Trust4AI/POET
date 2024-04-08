from typing import Optional
from pydantic_settings import BaseSettings

import os



class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: Optional[str] = None
    items_per_user: int = 50

    # Database settings
    database_hostname: str 
    database_port: str 
    database_password: str 
    database_name: str 
    database_username: str

    class Config:
        extra = "allow"
        env_file = os.path.join(os.path.dirname(__file__), '../../.env')
        env_file_encoding = "utf-8"


settings = Settings()
