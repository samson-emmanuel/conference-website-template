from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    INSTANCE_CONNECTION_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


Config = Settings()
