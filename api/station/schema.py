from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class BaseStation(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    line_id: Annotated[int, Field(ge=1)]
    capacity: Annotated[int, Field(ge=0)]


class SchemaStation(BaseStation):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(ge=1)]


class CreateStation(BaseStation):
    pass
