import os
import discord
import platform
from loguru import logger
from discord.ext import commands

from src.lifetime import _setup_db, _setup_logger, _shutdown_db
from src.utils.state import State
from src.settings import settings

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True

class DiscordClient(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=settings.command_prefix,
            intents=intents,
            help_command=None,
        )
        self.state = State()

        self.__startup()

        # Load extensions of application
        self.initial_extensions = ["src.events", "src.commands"]
        self.logger = logger.bind(extra_value="bot_client")

    def __startup(self):
        _setup_db(self)
        _setup_logger(self)

    async def __shutdown(self):
        await _shutdown_db(self)

    async def __load_extentions(self):
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                self.logger.success(f"Loaded extension: {extension}")
            except Exception as e:
                self.logger.error(str(e), task="load_extentions")

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}.")
        self.logger.info(f"`discord.py` module version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Logger Filter Level: {settings.log_level}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )

        await self.__load_extentions()

    async def close(self):
        print()
        await self.__shutdown()

    def startup(self, token: str, reconnect: bool = True) -> None:
        self.run(
            token,
            reconnect=reconnect,
            log_handler=self.logging_handler
        )
