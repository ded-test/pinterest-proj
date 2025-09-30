from app.schemas.photo import PhotoCreate, PhotoBase, PhotoUpdate, PhotoResponse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.models.user import User
from app.schemas.pin import PinCreate, PinResponse, PinUpdate
from app.crud.photo import PhotoCRUD
from app.crud.pin import PinCRUD
from app.security.auth import get_current_user
from app.models.pin import Pin


router = APIRouter(prefix="/api/pins", tags=["pins"])


@router.get("/", response_model=list[PinResponse])
async def get_all_pins(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[Pin]:

    try:
        all_pins = await PinCRUD.get_all_pins(db=db)
        return all_pins

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пины не найдены"
        )


@router.get("/{pin_id}", response_model=PinResponse)
async def get_pin_by_id(
    pin_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    pin = await PinCRUD.get_by_id(db, pin_id=pin_id)
    if not pin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пин не найден"
        )
    return pin


# Получить пин с полной информацией о пользователе и фото
@router.get("/{pin_id}/details", response_model=PinResponse)
async def get_pin_details(
    pin_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    pin = await PinCRUD.get_by_id_with_user(db, pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Пин не найден")
    return pin


@router.post("/", response_model=PinResponse, status_code=status.HTTP_201_CREATED)
async def create_pin(
    pin_data: PinCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    try:
        pin = await PinCRUD.create_pin(
            db=db, pin_data=pin_data, user_id=current_user.id
        )

        return pin

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании пина: {str(e)}",
        )


@router.put("/{pin_id}", response_model=PinResponse, status_code=status.HTTP_200_OK)
async def update_pin(
    pin_id: int,
    pin_data: PinUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    existing_pin = await PinCRUD.get_by_id(db, pin_id=pin_id)
    if not existing_pin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Исходный пин не найден"
        )

    if existing_pin.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления пина",
        )
    try:

        updated_pin = await PinCRUD.update_pin(db=db, pin_id=pin_id, pin_data=pin_data)

        if not updated_pin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пин не найден после обновления",
            )

        return updated_pin

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обновления пина: {str(e)}",
        )


@router.delete("/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pin(
    pin_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):

    existing_pin = await PinCRUD.get_by_id(db, pin_id=pin_id)
    if not existing_pin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пин не найден"
        )

    if existing_pin.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления пина",
        )
    try:
        deleted_pin = await PinCRUD.delete_pin(db, pin_id=pin_id)

        if not deleted_pin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Не удалось удалить пин"
            )
        return None

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Произошла ошибка удаления пина: {str(e)}",
        )
