import sys
import logging
from loguru import logger
from typing import TYPE_CHECKING
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


from src.settings import settings
from src.intercept_logging import InterceptHandler

if TYPE_CHECKING:
    from src.bot import DiscordClient

def _setup_db(bot: "DiscordClient") -> None:
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param bot: Disocrd Bot client.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    bot.state.db_engine = engine
    bot.state.db_session_factory = session_factory

async def _shutdown_db(bot: "DiscordClient") -> None:
    try:
        bot.logger.info("Clossing connection of database...")
        await bot.state.db_engine.dispose()
        bot.logger.success("Successfully closed connection of database.")
    except Exception as e:
            bot.logger.error(str(e), task="shutdown")

def _setup_logger(bot: "DiscordClient") -> None:
    bot.logging_handler = logging.basicConfig(
        handlers=[
            InterceptHandler(),
        ],
        level=0,
        force=True,
    )

    # Filter the log type of stdout in loguru
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.value,
    )
