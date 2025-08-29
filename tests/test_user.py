import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserCRUD
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserChangePassword , UserLogin
from app.security.password import verify_password
import sys
import os



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



def test_example():
    assert True


@pytest.mark.asyncio
async def test_create_user(db_session : AsyncSession):
    user_data = UserCreate(username='testuser',
                           password='Testpassword1',
                           email='testemail@example.com',
                           confirm_password='Testpassword1',
                           )
    
    user = await UserCRUD.create(db_session , user_data)

    assert user is not None
    assert user.username == 'testuser'
    assert user.email == 'testemail@example.com'
    assert await verify_password('Testpassword1' , user.hashed_password)