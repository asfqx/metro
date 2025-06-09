from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    async_scoped_session,
)
from asyncio import current_task
from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str = settings.db_url):
        self.engine = create_async_engine(url=url, echo=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scope_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )
        return session

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scope_session()
        yield session
        await session.close()

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()


db_helper = DatabaseHelper()
