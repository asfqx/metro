from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer
from . import Passenger, Line, Base


class Station(Base):
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    line_id: Mapped[int] = mapped_column(Integer, ForeignKey("lines.id"))
    capacity: Mapped[int] = mapped_column(nullable=False)

    line: Mapped[Line] = relationship("Line", back_populates="route")
    passengers: Mapped[list[Passenger]] = relationship(
        "Passenger", back_populates="station"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "line_id": self.line.name,
            "capacity": self.capacity,
            "line": self.line,
            "passengers": self.passengers,
            "count_of_passengers": len(self.passengers),
        }
