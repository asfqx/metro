from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Station
from .schema import CreateStation


async def create_station(session: AsyncSession, station_in: CreateStation) -> Station:
    station = Station(**station_in.model_dump())
    session.add(station)
    await session.commit()
    return station


async def get_stations(session: AsyncSession) -> list[Station]:
    stmt = select(Station).order_by(Station.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())
