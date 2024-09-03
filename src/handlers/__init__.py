__all__ = ("router")
from aiogram import Router
from handlers.scheduled_message import router as scheduled_messages_router
from handlers.user import router as users_router

router = Router(name=__name__)
router.include_router(scheduled_messages_router)
router.include_router(users_router)
