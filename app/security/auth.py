from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session
from app.crud.user import UserCRUD
from app.crud.jwt import jwt_crud
from app.models.user import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> User:

    # Dependency для получения текущего пользователя из access token

    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token не найден. Войдите в систему",
        )

    payload = await jwt_crud.check_token(token=access_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не валидный или просроченный access token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не валидный access token: не верный user id",
        )

    try:
        user = await UserCRUD.get_by_id(db=db, user_id=int(user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не валидный user_id в токене",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
