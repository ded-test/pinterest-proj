from app.schemas.photo import PhotoCreate , PhotoBase , PhotoUpdate , PhotoResponse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse
from app.crud.photo import PhotoCRUD
from app.crud.pin import PinCRUD
from app.security.auth import get_current_user

router = APIRouter(prefix='/api/photos', tags=['photos'])



@router.get('/', response_model=list[PhotoResponse])
async def get_all_photos(db : AsyncSession = Depends(get_db_session),
                         current_user : User = Depends(get_current_user)):

    all_photos = await PhotoCRUD.get_all_photos(db)
    return all_photos


@router.get('/{photo_id}' , response_model=PhotoResponse)
async def get_photo_by_id( photo_id : int,
                          
                           db : AsyncSession = Depends(get_db_session),
                            
                          current_user : User = Depends(get_current_user)
                           ):
    
    photo = await PhotoCRUD.get_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Фото не найдено')
    return photo
    

@router.post('/' , response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    photo_data : PhotoCreate,
    db : AsyncSession = Depends(get_db_session),
    current_user : User = Depends(get_current_user)
    ):
    try:
        pin = await PinCRUD.get_by_id(db, photo_data.pin_id)
        if not pin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Пин не найден')
        
        if pin.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Недостаточно прав для создания фото к этому пину')
        
        photo = await PhotoCRUD.create_photo(db=db , photo_data=photo_data, pin_id = photo_data.pin_id)
        return photo
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Ошибка при создании фото: {e}')
    

@router.post('/pins/{pin_id}/photos' , response_model=PhotoResponse , status_code=status.HTTP_201_CREATED)
async def add_photo_to_pin(
    pin_id : int,
    photo_data : PhotoCreate,
    db : AsyncSession = Depends(get_db_session),
    current_user : User = Depends(get_current_user)
):
    pin = await PinCRUD.get_by_id(db , pin_id)
    if not pin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пин не найден')
    
    if pin.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Недостаточно прав для добавления фото к этому пину')
    

    try:
        photo = await PinCRUD.add_photo_to_pin(db=db , photo_data=photo_data , pin_id= pin_id)
        return photo
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Ошибка при добавлении фото: {str(e)}')
    

@router.put('/{photo_id}' , response_model=PhotoResponse)
async def update_photo(photo_id : int,
                       photo_data : PhotoUpdate,
                       db : AsyncSession = Depends(get_db_session),
                       current_user : User = Depends(get_current_user)):
    
    existing_photo = await PhotoCRUD.get_by_id(db=db, photo_id=photo_id)
    if not existing_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Фото не найдено')
    
    pin = await PinCRUD.get_by_id(db, pin_id=existing_photo.pin_id)

    if pin.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Недостаточно прав для редактирования этого фото')

    updated_photo = await PhotoCRUD.update_photo(db=db,
                                     photo_id=photo_id, 
                                     photo_update=photo_data)
    if not updated_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Фото не найдено')
    return updated_photo  
      
    
    

@router.delete('/{photo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id : int,
                       db : AsyncSession=Depends(get_db_session),
                       current_user: User = Depends(get_current_user)):
    
    existing_photo = await PhotoCRUD.get_by_id(db=db, photo_id=photo_id)
    if not existing_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Фото не найдено')
    
    pin = await PinCRUD.get_by_id(db, existing_photo.pin_id)

    if not pin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пин не найден')
    
    if pin.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Недостаточно прав для удаления фото')
    
    result = await PhotoCRUD.delete_photo(db=db, photo_id=photo_id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Произошла ошибка удаления фото')
    return None
    
    

    
    
    
    


    
