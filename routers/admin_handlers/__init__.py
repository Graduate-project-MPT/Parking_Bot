__all__ = ("router",)

from aiogram import Router
from .common_handlers import router as common_router
# from .user_commands import router as user_commands_router

router = Router(name=__name__)

router.include_routers(
    common_router
)
