from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated


class BaseLine(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]


class Line(BaseLine):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(ge=1)]


class CreateLine(BaseLine):
    pass
