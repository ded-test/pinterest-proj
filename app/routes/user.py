from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from schemas.user import UserCreate, UserResponse
from crud.user import UserCRUD

app = APIRouter()


@app.post("/api/registration", response_model=UserResponse)
async def registration(
    user_create: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    result = await UserCRUD.create(db=db, user_create=user_create)
    return result
