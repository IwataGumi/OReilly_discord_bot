from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import create_async_engine


from src.settings import settings


async def drop_database() -> None:
    db_url = make_url(str(settings.db_url))
    engine = create_async_engine(
        db_url,
        isolation_level="AUTOCOMMIT"
    )

    print(engine.url.database)
