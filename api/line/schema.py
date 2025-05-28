from pydantic import BaseModel, ConfigDict


class BaseLine(BaseModel):
    name: str


class Line(BaseLine):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CreateLine(BaseLine):
    pass
