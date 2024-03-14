import enum
from pathlib import Path
from typing import Literal, Optional
from zoneinfo import ZoneInfo
from tempfile import gettempdir

from yarl import URL
from pydantic_settings import BaseSettings, SettingsConfigDict

TEMP_DIR = Path(gettempdir())


EnvironmentType = Literal["dev", "prod"]


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    # Current environment
    environment: EnvironmentType = "dev"
    log_level: LogLevel

    # Discord Bot
    owner_id: int
    discord_token: str
    command_prefix: str = "/"

    # Variables for the database
    db_scheme: str = "sqlite+aiosqlite"
    db_host: str = ""
    db_port: int | None = None
    db_user: str | None = None
    db_pass: str | None = None
    db_base: str = "//./discord_bot.db"

    db_echo: bool | None = True

    time_zone: ZoneInfo = ZoneInfo("Asia/Tokyo")

    @property
    def is_production(self) -> bool:
        return self.environment != "dev"

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme=self.db_scheme,
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BOT_",
        env_file_encoding="utf-8",
    )


settings = Settings()