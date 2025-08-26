from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas.user import UserCreate

app = APIRouter()


@app.post("/api/registration", response_model=UserCreate)
async def registration(db: AsyncSession = Depends(get_db_session)):
    