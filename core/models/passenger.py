from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from typing import List
from . import Station, Train, Base


class Passenger(Base):
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    start_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    end_st_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    current_station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"))
    status: Mapped[str] = mapped_column(String(8), nullable=False)

    station: Mapped[Station] = relationship("Station", back_populates="passengers")
    train: Mapped[List[Train]] = relationship("Train", back_populates="passengers_now")

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
