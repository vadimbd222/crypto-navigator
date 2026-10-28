"""Сервис новостей: CryptoCompare API (этап 7)."""

import logging

import config
from utils.http import ServiceError, fetch_json

API_URL = "https://min-api.cryptocompare.com/data/v2/news/"

log = logging.getLogger(__name__)


async def get_latest_news(limit: int = 5) -> list[dict]:
    """Свежие новости о криптовалютах. Возвращает список словарей.

    Бросает ServiceError, если API ответил ошибкой (плохой ключ, лимит и т.п.).
    """
    params = {"lang": "EN"}
    headers = {}
    if config.CRYPTOCOMPARE_API_KEY:
        # CryptoCompare принимает ключ двумя способами — шлём обоими:
        params["api_key"] = config.CRYPTOCOMPARE_API_KEY
        headers["authorization"] = f"Apikey {config.CRYPTOCOMPARE_API_KEY}"

    raw = await fetch_json(API_URL, params=params, headers=headers)

    data = raw.get("Data")
    if not isinstance(data, list):
        # При ошибке CryptoCompare присылает не список, а {"Data": {}, "Err": {...}}
        # (в старом формате: {"Response": "Error", "Message": "..."}).
        msg = raw.get("Message") or ""
        if not msg and isinstance(raw.get("Err"), dict):
            msg = raw["Err"].get("message", "")
        log.warning(f"CryptoCompare вернул ошибку: {msg or raw}")
        raise ServiceError(msg or "сервис новостей недоступен")

    news = []
    for item in data[:limit]:
        source = item.get("source_info", {}).get("name") or item.get("source", "")
        news.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": source,
        })
    return news