from enum import Enum
from typing import Optional, Annotated
from core.models.Status import Status
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, Field


class BasePassenger(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    status: Status
    start_st_id: Annotated[int, Field(ge=1)]
    end_st_id: Annotated[int, Field(ge=1)]
    train_id: Optional[int] = None
    current_station_id: Optional[int] = None

    @field_validator("current_station_id", "train_id")
    def validator_current_station_train_id(cls, value):
        if value is None:
            return None
        else:
            if value < 1 or not isinstance(value, int):
                raise ValidationError(
                    "Value must be an integer and greater than or equal to 1."
                )
            else:
                return value


class Passenger(BasePassenger):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CreatePassenger(BasePassenger):
    pass
