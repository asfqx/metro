from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.db_helper import db_helper
from .schema import TrainCreate, TrainSchema
from .crud import create_train, get_trains

router = APIRouter(prefix="/train", tags=["train"])


@router.get("/", response_model=list[TrainSchema])
async def r_get_trains(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_trains(session)


@router.post("/", response_model=TrainSchema)
async def r_create_train(
    train_in: TrainCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await create_train(session, train_in)
