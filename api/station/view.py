from fastapi import APIRouter, Depends
from core.database.db_helper import db_helper
from .crud import get_stations, create_station
from .schema import CreateStation, SchemaStation

router = APIRouter(prefix="/station", tags=["station"])


@router.get("/", response_model=list[SchemaStation])
async def r_get_stations(session=Depends(db_helper.scoped_session_dependency)):
    return await get_stations(session)


@router.post("/", response_model=SchemaStation)
async def r_create_station(
    station_in: CreateStation, session=Depends(db_helper.scoped_session_dependency)
):
    station = await create_station(session, station_in)
    return station
