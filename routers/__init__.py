__all__ = ("router",)

from aiogram import Router
from .callback import router as callback_router
from .commands import router as commands_router
from .admin_handlers import router as admin_router
from .employee_handlers import router as employee_router
from .user_handlers import router as user_router

router = Router(name=__name__)

router.include_routers(
    callback_router,
    admin_router,
    user_router,
    employee_router,
    commands_router,
)
