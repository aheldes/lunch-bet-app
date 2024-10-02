from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the application
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_USERNAME: str
    DB_PASSWORD: str


settings = Settings()
