from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.crud.user import UserCRUD
from app.crud.jwt import jwt_crud
from app.security.jwt import jwt_manager

app = APIRouter()


@app.post("/api/registration", response_model=UserResponse)
async def registration(
    user_create: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    result = await UserCRUD.create(db=db, user_create=user_create)
    return {
        "message": "Вход в систему прошел успешно",
        "user": {result},
    }


@app.post("/api/authentication")
async def authentication(
    user_login: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    user = await UserCRUD.authenticate(db=db, user_login=user_login)
    try:
        access_token = await jwt_crud.create_access_token(user=user)
        refresh_token = await jwt_crud.create_refresh_token(user=user, db=db)

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
            "message": "Вход в систему прошел успешно",
            "user": {"id": user.id, "username": user.username},
        }
    except Exception as e:
        raise


@app.get("/api/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен Refresh не найден"
        )

    payload = await jwt_crud.check_token(token=refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недопустимый refresh token",
        )

    user_id = int(payload.get("sub"))
    user = await UserCRUD.get_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    access_token = await jwt_crud.create_access_token(user=user)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # фиксани, False только для теста
        samesite="lax",
        max_age=jwt_manager.access_expire * 60,
    )

    return {
        "message": "Токен успешно обновлен",
        "user": {"id": user.id, "username": user.username},
    }
