from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from starlette.responses import HTMLResponse
from .passenger.crud import get_passengers
from .train.crud import get_trains
from .station.crud import get_stations
from core.database.db_helper import db_helper
from .line.view import router as line_router
from .passenger.view import router as passenger_router
from fastapi import APIRouter
from .station.view import router as station_router
from .train.view import router as train_router
from .line.view import get_lines

router = APIRouter(prefix="/api")
router.include_router(line_router)
router.include_router(passenger_router)
router.include_router(station_router)
router.include_router(train_router)


@router.get("/", response_class=HTMLResponse)
async def get_all(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    passengers = await get_passengers(session)
    trains = await get_trains(session)
    stations = await get_stations(session)
    lines = await get_lines(session)
    data = {}
    for passenger in passengers:
        data["Passengers"][passenger.id] = {
            "start_st_id": passenger.start_st_id,
            "end_st_id": passenger.end_st_id,
            "current_station": passenger.station.id,
            "train": passenger.train.id,
            "status": passenger.status,
        }

    for station in stations:
        data["Stations"][station.id] = {
            "name": station.name,
            "line": station.line.name,
            "capacity": station.capacity,
            "passengers": [passenger.id for passenger in station.passengers],
        }

    for line in lines:
        data["Lines"][line.id] = {
            "name": line.name,
            "stations": [station_id for station_id in line.route.id],
            "trains": [train_id for train_id in line.trains_on_line.id],
        }
    for train in trains:
        data["Trains"][train.id] = {
            "route": train.line_for_train.route,
            "line": train.line_for_train,
            "capacity": train.capacity,
            "current_station_id": train.current_station_id,
        }
    return data
