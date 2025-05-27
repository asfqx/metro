from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True, nullable=False)
