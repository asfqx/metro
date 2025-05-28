from enum import Enum
from typing import Optional

from pydantic import BaseModel
from fastapi import Path


class Status(Enum):
    WAITING = "WAITING"
    IN_TRAIN = "IN TRAIN"
    FINISHED = "FINISHED"


class BasePassenger(BaseModel):
    name: str
    status: Status
    start_st_id: int
    end_st_id: int
    current_station_id: Optional[int]
    train_id: Optional[int]


class Passenger(BasePassenger):
    id: int


class CreatePassenger(BasePassenger):
    pass
