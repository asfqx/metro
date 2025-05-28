from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str = settings.db_url):
        self.engine = create_async_engine(url=url, echo=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()


db_helper = DatabaseHelper()
