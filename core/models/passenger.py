from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from typing import List
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import Train, Station

from .Base import Base


class Passenger(Base):
    name: Mapped[str] = mapped_column(String(20))
    start_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    end_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    current_station_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stations.id"), nullable=True
    )
    train_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("trains.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String)

    station: Mapped["Station"] = relationship(
        "Station",
        back_populates="passengers",
        foreign_keys="Passenger.current_station_id",
    )
    train: Mapped[Optional["Train"]] = relationship(
        "Train", back_populates="passengers_now"
    )
