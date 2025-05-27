from pydantic import BaseModel


class BaseLine(BaseModel):
    name: str


class Line(BaseLine):
    id: int


class CreateLine(BaseLine):
    pass
