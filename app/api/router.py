from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from libs.conf import settings

v1 = APIRouter(prefix=settings.API_V1_STR)
v1.include_router(chat_router)