from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from typing import List
import typing

if typing.TYPE_CHECKING:
    from . import Train, Station

from .Base import Base


class Passenger(Base):
    name: Mapped[str] = mapped_column(String(20))
    start_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    end_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    current_station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"))
    status: Mapped[str] = mapped_column(String(8))

    station: Mapped["Station"] = relationship(
        "Station",
        back_populates="passengers",
        foreign_keys="Passenger.current_station_id",
    )
    train: Mapped[List["Train"]] = relationship(
        "Train", back_populates="passengers_now"
    )

    def to_dict(self):
        if self.status == "waiting":
            return {
                "id": self.id,
                "name": self.name,
                "origin_id": self.start_st_id,
                "destination_id": self.end_st_id,
                "current_station_id": self.station.name,
                "status": self.status,
            }
        else:
            return {
                "id": self.id,
                "name": self.name,
                "origin_id": self.start_st_id,
                "destination_id": self.end_st_id,
                "current_train_id": self.train.id,
                "status": self.status,
            }
