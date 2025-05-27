from sqlalchemy.ext.asyncio import AsyncSession
from api.line.schema import CreateLine, Line
from sqlalchemy import select


def create_passenger(session: AsyncSession, passenger_in: CreateLine):
    line = Line(**line_in.model_dump())
    session.add(line)
    session.commit()
    return line


def get_line(session: AsyncSession, line_id: int) -> Line:
    return session.get(Line, select(Line).where(Line.id == line_id))


def get_lines(session: AsyncSession) -> List[Line]:
    stmt = select(Line).order_by(Line.id)
    result: Result = session.execute(stmt)
    return result.scalars().all()


def delete_line(session: AsyncSession, line_id: int):
    stmt = delete(Line).where(Line.id == line_id)
    session.execute(stmt)
    session.commit()

