from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)
from sqlalchemy.orm import scoped_session
from asyncio import current_task
from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str = settings.db_url):
        self.engine = create_async_engine(url=url, echo=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scoped_session(self):
        session = scoped_session(
            sessionmaker=self.session_factory, scopefunc=current_task
        )
        return session

    async def session_dependency(self):
        session = self.get_scoped_session()
        async with session() as session:
            yield session
            await session.remove()


db_helper = DatabaseHelper()
