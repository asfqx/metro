from pydantic import BaseModel
from fastapi import Path


class Status(Enum):
    WAITING = 'WAITING'
    IN_TRAIN = 'IN TRAIN'
    FINISHED = 'FINISHED'
class BasePassenger(BaseModel):
    name: str
    status: Status



class Line(BaseLine):
    id: int


class CreateLine(BaseLine):
    pass
