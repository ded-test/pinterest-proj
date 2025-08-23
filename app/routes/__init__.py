from fastapi import APIRouter
from routes.photo_views import router as photo_router

router = APIRouter()

router.include_router(router=photo_router, prefix="/photos")
