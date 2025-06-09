from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
import typing

if typing.TYPE_CHECKING:
    from .station import Station
    from .train import Train
from .Base import Base


class Line(Base):
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    route: Mapped[list["Station"]] = relationship(
        "Station", back_populates="line", order_by="Station.id"
    )
    trains_on_line: Mapped[list["Train"]] = relationship(
        "Train", back_populates="line_for_train"
    )
