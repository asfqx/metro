from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer
import typing

if typing.TYPE_CHECKING:
    from .lines import Line
    from .passenger import Passenger
from .Base import Base


class Station(Base):
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    line_id: Mapped[int] = mapped_column(Integer, ForeignKey("lines.id"))
    capacity: Mapped[int] = mapped_column(nullable=False)

    line: Mapped["Line"] = relationship("Line", back_populates="route")
    passengers: Mapped[list["Passenger"]] = relationship(
        "Passenger",
        back_populates="station",
        foreign_keys="Passenger.current_station_id",
    )
