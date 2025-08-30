from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from app.core.templates import templates

from app.core.dependencies import get_db_session
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import UserCRUD

app = APIRouter()


@app.post("/api/registration", response_model=UserResponse)
async def registration(
    user_create: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    result = await UserCRUD.create(db=db, user_create=user_create)
    return result


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})
