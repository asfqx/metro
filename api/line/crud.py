from sqlalchemy.ext.asyncio import AsyncSession
from api.line.schema import CreateLine, Line as SchemaLine
from sqlalchemy import select, Result
from core.models.lines import Line
from typing import Optional


async def create_line(session: AsyncSession, line_in: CreateLine) -> Line:
    line = Line(**line_in.model_dump())
    session.add(line)
    await session.commit()
    return line


async def get_line(session: AsyncSession, line_id: int) -> Optional[SchemaLine]:
    return await session.get(Line, line_id)


async def get_lines(session: AsyncSession) -> list[SchemaLine]:
    stmt = select(Line).order_by(Line.id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())
