from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Passenger
from api.passenger.schema import Passenger as SchemaPassenger, CreatePassenger


async def get_passengers(session: AsyncSession) -> list[SchemaPassenger]:
    stmt = select(Passenger).order_by(Passenger.id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_passenger(
    passenger_in: CreatePassenger, session: AsyncSession
) -> Passenger:
    passenger = Passenger(**passenger_in.model_dump())
    if passenger.current_station_id is None:
        passenger.current_station_id = passenger.start_st_id
    passenger.status = passenger.status.value
    session.add(passenger)
    await session.commit()
    return passenger
