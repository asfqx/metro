from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_helper import db_helper
from .schema import CreatePassenger, Passenger
from .crud import create_passenger, get_passengers

router = APIRouter(tags=["Passenger"], prefix="/passenger")


@router.post("/", response_model=CreatePassenger)
async def route_create_passenger(
    passenger_in: CreatePassenger,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await create_passenger(session=session, passenger_in=passenger_in)


@router.get("/", response_model=list[Passenger])
async def route_get_passengers(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_passengers(session=session)
