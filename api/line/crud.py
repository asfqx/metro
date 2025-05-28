from sqlalchemy.ext.asyncio import AsyncSession
from api.line.schema import CreateLine
from sqlalchemy import select, Result, delete
from core.models import Line
from typing import Optional


async def create_passenger(session: AsyncSession, line_in: CreateLine):
    line = Line(**line_in.model_dump())
    session.add(line)
    await session.commit()
    return line


async def get_line(session: AsyncSession, line_id: int) -> Optional[Line]:
    return await session.get(Line, line_id)


async def get_lines(session: AsyncSession) -> list[Line]:
    stmt = select(Line).order_by(Line.id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())


def delete_line(session: AsyncSession, line_id: int):
    stmt = delete(Line).where(Line.id == line_id)
    session.execute(stmt)
    session.commit()
