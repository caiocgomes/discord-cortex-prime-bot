from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CORTEX_BOT_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    token: SecretStr = SecretStr("")
    db: str = "cortex_bot.db"


settings = Settings()
