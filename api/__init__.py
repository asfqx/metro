from .line.view import router as line_router
from .passenger.view import router as passenger_router
from fastapi import APIRouter


router = APIRouter(prefix="/api")
router.include_router(line_router)
router.include_router(passenger_router)
