from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    API_TITLE: str = Field(default="PET Saúde - API")
    ENV: str = Field(default="dev")
    DATABASE_URL: str
    CORS_ORIGINS: str = Field(default="*")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
