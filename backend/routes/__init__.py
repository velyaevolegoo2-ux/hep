"""Routes package for Hep"""

from .orders import router as orders_router
from .translate import router as translate_router
from .telegram import router as telegram_router
from .simple_auth import router as simple_auth_router
from .rephrase import router as rephrase_router

__all__ = [
    "orders_router",
    "translate_router", 
    "telegram_router",
    "simple_auth_router",
    "rephrase_router"
]
