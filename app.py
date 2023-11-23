import asyncio

import uvicorn
from app.router import router
from app.utils import create_tables, rabbit
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(docs_url="/")
    app.include_router(router)

    @app.on_event("startup")
    async def startup_event():
        await create_tables()
        loop = asyncio.get_running_loop()
        task = loop.create_task(rabbit.consume(loop))
        await task

    return app


def main() -> None:
    uvicorn.run(
        f"{__name__}:create_app",
        host="0.0.0.0",
        port=8888,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    main()
