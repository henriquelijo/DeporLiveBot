# src/adapters/__init__.py
from .json_repository import JSONMatchRepository
from .api_football import ApiFootballAdapter
from .telegram_bot import TelegramBotAdapter

__all__ = [
    "JSONMatchRepository",
    "ApiFootballAdapter",
    "TelegramBotAdapter"
]