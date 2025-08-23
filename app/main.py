from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from database import db_manager, redis_manager

# from routes import router as photo_router
from config import settings
from models.base import Base


DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Start application")
    try:
        print("INFO:     Init DB")
        db_manager.init_db(database_url=DATABASE_URL)

        print("INFO:     Create DB tables")
        await db_manager.create_tables()

        print("INFO:     Init Redis")
        await redis_manager.init_redis(database_url=REDIS_URL)

        print("INFO:     Application up")

    except Exception as e:
        print(f"ERROR:     Startup failed: {e}")
        raise

    yield

    print("INFO:     Shutdown...")
    print("INFO:     Application stopped successfully")


app = FastAPI(lifespan=lifespan)
# app.include_router(router=photo_router, prefix="/api/photo")


@app.get("/")
def start():
    return {"message": "Go to /docs#/"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
