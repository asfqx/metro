from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .schema import TrainCreate
from core.models import Train


async def create_train(session: AsyncSession, train_in: TrainCreate) -> Train:
    train = Train(**train_in.model_dump())
    session.add(train)
    await session.commit()
    return train


async def get_trains(session: AsyncSession) -> list[Train]:
    stmt = select(Train).order_by(Train.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())
