from .auth import app as auth_router
from .photo_views import router as photo_router
from .pin import router as pin_router

__all__ = [
    "auth_router",
    "photo_router",
    "pin_router"

]
