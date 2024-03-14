import glob
import os
from typing import AsyncGenerator
import pytest_asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


from src.db.utils import drop_database
from src.settings import settings
from src.bot import DiscordClient

@pytest_asyncio.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from src.db.meta import meta  # noqa: WPS433
    from src.db.models import load_all_models  # noqa: WPS433

    load_all_models()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()

@pytest_asyncio.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()

@pytest_asyncio.fixture
async def bot(dbsession: AsyncSession):
    # Setup
    bot = DiscordClient()

    await bot._async_setup_hook()

    dpytest.configure(bot)

    yield bot

    # Teardown
    await dpytest.empty_queue() # empty the global message queue as test teardown

def pytest_sessionfinish(session, exitstatus):
    """ Code to execute after all tests. """

    # dat files are created when using attachements
    print("\n-------------------------\nClean dpytest_*.dat files")
    fileList = glob.glob('./dpytest_*.dat')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except Exception:
            print("Error while deleting file : ", filePath)
