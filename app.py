import uvicorn
from fastapi import FastAPI
from app.utils import settings_rabbit, read_messages, create_tables
from app.router import router
from threading import Thread



def create_app():
    app = FastAPI(docs_url='/')
    app.include_router(router)

    @app.on_event('startup')
    async def startup_event():
        settings_rabbit()
        create_tables()
        new_thread = Thread(target=read_messages)
        new_thread.start()

    return app

def main():
    uvicorn.run(
        f"{__name__}:create_app",
        host='0.0.0.0', port=8888,
        log_level='debug'
    )

if __name__ == '__main__':
    main()

