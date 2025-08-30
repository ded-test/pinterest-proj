from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

# from routes import router as photo_router
from app.core.database import db_manager, redis_manager
from app.services.chat import manager
from app.routes import (
    user_router,
)
from app.core.config import settings
from app.models.base import Base
from app.core.logger_config import get_logger
from fastapi.responses import HTMLResponse
from app.core.templates import templates

logger = get_logger(__name__)

DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Старт приложения")
    try:
        logger.info("Запуск БД")
        db_manager.init_db(database_url=DATABASE_URL)

        logger.info("Создание таблиц")
        await db_manager.create_tables()

        logger.info("Запуск Redis")
        await redis_manager.init_redis(database_url=REDIS_URL)

        logger.info("Приложение запущено")

    except Exception as e:
        logger.error(f"Ошибка запуска приложения: {e}")
        raise

    yield

    logger.info("Остановка...")
    logger.info("Приложение успешно остановлено")


app = FastAPI(lifespan=lifespan)
app.include_router(router=user_router)
# app.include_router(router=photo_router, prefix="/api/photo")


@app.websocket("/ws/chat")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"Пользователь сказал: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/")
def start():
    return {"message": "Перейди в /docs#/"}


@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
