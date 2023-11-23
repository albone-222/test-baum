from typing import List

from fastapi import APIRouter, BackgroundTasks, UploadFile
from fastapi.responses import JSONResponse

from .schemas import ResultCounter
from .utils import get_data, send_file

router = APIRouter()


@router.post("/counter", description="Только файлы в формате TXT")
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
    if file.filename.split(".")[-1] != "txt":
        return JSONResponse(
            content={"message": "Сервис принимает только файлы в формате TXT"},
            status_code=400,
        )
    background_tasks.add_task(send_file, file)
    return f"Файл {file.filename} принят в обработку"


@router.get("/get_counter", response_model=List[ResultCounter])
async def get_counter():
    return await get_data()
