from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Get the directory where this config file is located
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # deAPI Configuration
    deapi_api_key: str = ""
    deapi_base_url: str = "https://api.deapi.ai"
    
    # iFlow API Configuration (for Prompt Enhancement)
    iflow_api_key: str = ""
    iflow_base_url: str = "https://apis.iflow.cn/v1"
    
    # Database
    database_url: str = f"sqlite:///{BASE_DIR / '..' / 'videlo.db'}"

    class Config:
        env_file = str(BASE_DIR / ".." / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
