import asyncio
from datetime import datetime
from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from .exeption import RemoteServerError
from .utils import push_message, send_file
# from .schemas import UploadFileWithText

router = APIRouter()


@router.post("/counter", description='Только файлы в формате TXT')
async def upload(file: UploadFile):
    if file.filename.split('.')[-1] != 'txt':
        return JSONResponse(content={'message': 'Сервис принимает только файлы в формате TXT'}, status_code=400)
    
    await send_file(file)
    # with file.file as f:
    #     f = f.read().decode("utf-8").split("\n")
    #     title = None
    #     for line in f:
    #         if title is None:
    #             title = line.strip()
    #         message = {'datetime': datetime.now().isoformat(),
    #                    'title': title,
    #                    'text': line.strip().replace('\xa0', ' '),
    #                    }
    #         push_message(str(message))
    #         await asyncio.sleep(1)
    return f'Файл {file.filename} принят в обработку'


