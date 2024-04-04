__all__ = ("router",)

from aiogram import Router
from .help_handlers import router as help_router
from .auth_handlers import router as auth_router
from .reserve_handlers import router as reserve_router

router = Router(name=__name__)

router.include_routers(
    auth_router,
    reserve_router,
    help_router,
)