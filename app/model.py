from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from .schemas import CheckLine


class Lines(Base):
    # Модель таблицы БД со строками текста
    __tablename__ = "lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime = mapped_column(DateTime)
    title: Mapped[str] = mapped_column(index=True)
    text: Mapped[str]
    x_in_line: Mapped[int]

    def __init__(self, data: CheckLine):
        self.datetime = data.datetime
        self.title = data.title
        self.text = data.text
        self.x_count()

    def x_count(self):
        self.x_in_line = self.text.lower().count("х")
