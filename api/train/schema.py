from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, Annotated


class TrainBase(BaseModel):
    capacity: Annotated[int, Field(ge=0)]
    current_station_id: Annotated[int, Field(ge=1)]
    line_id: Annotated[int, Field(ge=1)]


class TrainSchema(TrainBase):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(ge=1)]


class TrainCreate(TrainBase):
    pass
