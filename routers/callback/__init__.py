__all__ = ("router",)

from aiogram import Router
from .base_callback import router as base_callback_router

router = Router(name=__name__)

router.include_routers(
    base_callback_router,
)