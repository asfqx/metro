from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Line
from api.line.schema import CreateLine


def create_line(session: AsyncSession, line_in: CreateLine):
    line = Line(**line_in.model_dump())
    session.add(line)
    session.commit()
    return line
