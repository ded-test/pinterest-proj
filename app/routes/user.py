from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from app.core.templates import templates

from app.core.dependencies import get_db_session
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.crud.user import UserCRUD

app = APIRouter()


@app.post("/api/registration", response_model=UserResponse)
async def registration(
    user_create: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    result = await UserCRUD.create(db=db, user_create=user_create)
    return result


@app.post("/api/authentication", response_model=UserResponse)
async def authentication(
    user_login: UserLogin, db: AsyncSession = Depends(get_db_session)
):
    user = await UserCRUD.authenticate(db=db, user_login=user_login)
    return user
