import asyncio
from datetime import datetime

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select

from .db import SessionLocal, engine
from .init_db import Base
from .model import Lines
from .rabbit_client import RabbitMQ
from .schemas import CheckLine, ResultCounter


def validation_message(message: dict) -> CheckLine:
    try:
        validate_m = CheckLine(**message)
    except ValueError:
        raise HTTPException(message="Ошибка в валидации данных", status_code=400)
    return validate_m


async def save_message(message: CheckLine) -> None:
    async with SessionLocal() as session:
        session.add(Lines(message))
        await session.commit()


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def read_messages(message) -> None:
    message = eval(message)
    message = validation_message(message)
    asyncio.create_task(save_message(message))


async def get_data() -> list[ResultCounter]:
    async with SessionLocal() as session:
        query = (
            select(
                func.min(Lines.datetime).label("datetime"),
                Lines.title,
                func.avg(Lines.x_in_line).label("x_avg_count_in_line"),
            )
            .select_from(Lines)
            .group_by(Lines.title)
        )
        res = await session.execute(query)
        result = res.all()
        return [ResultCounter.model_validate(r._asdict()) for r in result]


rabbit = RabbitMQ(read_messages)


async def send_file(file: UploadFile) -> None:
    with file.file as f:
        f = f.read().decode("utf-8").split("\n")
        title = None
        for line in f:
            if title is None:
                title = line.strip()
            message = {
                "datetime": datetime.now().isoformat(),
                "title": title,
                "text": line.strip().replace("\xa0", " "),
            }
            await rabbit.send_message(message)
            await asyncio.sleep(3)
