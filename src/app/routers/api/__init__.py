__all__ = ("router",)

from fastapi import APIRouter

from .chat import router as chats_router

router = APIRouter(prefix="/api", tags=["api"])
router.include_router(chats_router)
