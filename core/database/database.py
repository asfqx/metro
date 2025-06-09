from .db_helper import db_helper
from core.models.Base import Base


async def setup_database():
    async with db_helper.engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
