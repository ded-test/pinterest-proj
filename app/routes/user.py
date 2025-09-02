from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

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


@app.post("/api/authentication")
async def authentication(
    user_login: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    user = await UserCRUD.authenticate(db=db, user_login=user_login)
    try:

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # фиксани, False только для теста
            samesite="lax",
            max_age=jwt_manager.access_expire * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # фиксани, False только для теста
            samesite="strict",
            max_age=jwt_manager.refresh_expire * 60,
        )

        return {
            "message": "Login successful",
            "user": {"id": user.id, "username": user.username},
        }
    except Exception as e:
        raise
