from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = Field(default="development")

    database_url: str
    
    secret_key: str = Field(..., min_length=32)
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FATS_",
        extra="ignore"
    )

