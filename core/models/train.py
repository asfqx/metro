from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import typing

if typing.TYPE_CHECKING:
    from .passenger import Passenger
    from .lines import Line

from .Base import Base


class Train(Base):
    capacity: Mapped[int] = mapped_column(Integer)
    current_station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    line_id: Mapped[int] = mapped_column(ForeignKey("lines.id"))

    line_for_train: Mapped["Line"] = relationship(
        "Line", back_populates="trains_on_line"
    )
    passengers_now: Mapped[list["Passenger"]] = relationship(
        "Passenger", back_populates="train"
    )
