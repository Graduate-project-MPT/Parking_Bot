__all__ = ("router",)

from aiogram import Router
from .reserve import router as reserve_router

router = Router(name=__name__)

router.include_routers(
    reserve_router,
)