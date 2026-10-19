from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    database_url: str = "sqlite:///./restaurant.db"
    timezone: str = "Asia/Karachi"          # the restaurant's local time zone
    admin_username: str = "admin"
    admin_password: str = "lol"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    chat_model: str = "openai/gpt-4o-mini"

    @property
    def sqlalchemy_url(self) -> str:
        # Some hosts give "postgres://", but SQLAlchemy needs "postgresql://"
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


settings = Settings()