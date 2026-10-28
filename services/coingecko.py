"""Сервис курсов: CoinGecko API + кэш TTL 60 секунд."""

import time
import logging

from utils.http import fetch_json, ServiceError

logger = logging.getLogger(__name__)

API_URL = "https://api.coingecko.com/api/v3"

POPULAR_COINS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "toncoin": "Toncoin",
    "solana": "Solana",
    "dogecoin": "Dogecoin",
    "cardano": "Cardano",
}

# Короткие имена, которые понимает бот: btc -> bitcoin и т.д.
SYMBOL_ALIASES = {
    "btc": "bitcoin", "bitcoin": "bitcoin",
    "eth": "ethereum", "ethereum": "ethereum",
    "ton": "toncoin", "toncoin": "toncoin",
    "sol": "solana", "solana": "solana",
    "doge": "dogecoin", "dogecoin": "dogecoin",
    "ada": "cardano", "cardano": "cardano",
}

FIATS = ("usd", "eur", "rub")

CACHE_TTL = 60  # секунд — кэш, чтобы не долбить API каждый раз

# Кэш: {coin_id: (время записи, данные)}
_cache: dict = {}


def fmt(value: float) -> str:
    """Красивый формат числа: 67 432 или 0.5."""
    if value >= 1000:
        return f"{value:,.0f}".replace(",", " ")
    if value >= 1:
        return f"{value:,.2f}".replace(",", " ")
    return f"{value:.6f}".rstrip("0")


async def get_rate(coin_id: str, vs: str) -> float:
    """Цена 1 монеты в заданной валюте."""
    params = {"ids": coin_id, "vs_currencies": vs}
    raw = await fetch_json(f"{API_URL}/simple/price", params=params)
    try:
        return float(raw[coin_id][vs])
    except (KeyError, TypeError) as exc:
        raise LookupError(f"монета не найдена: {coin_id}") from exc


async def get_prices(coin_id: str) -> dict:
    """Цены монеты в usd/eur/rub. Повторные запросы берутся из кэша (60 сек)."""
    now = time.monotonic()
    if coin_id in _cache:
        cached_at, cached_data = _cache[coin_id]
        if now - cached_at < CACHE_TTL:
            data = dict(cached_data)
            data["from_cache"] = True
            logger.info("Кэш попал: %s", coin_id)
            return data

    params = {
        "ids": coin_id,
        "vs_currencies": ",".join(FIATS),
        "include_24hr_change": "true",
    }
    raw = await fetch_json(f"{API_URL}/simple/price", params=params)
    if coin_id not in raw:
        raise LookupError(f"монета не найдена: {coin_id}")

    data = {"name": POPULAR_COINS.get(coin_id, coin_id), "prices": raw[coin_id], "from_cache": False}
    _cache[coin_id] = (now, data)
    logger.info("Цены получены и закэшированы: %s", coin_id)
    return data


async def convert(amount: float, base: str, quote: str) -> tuple[float, str]:
    """Конвертация монета<->валюта (usd, eur, rub)."""
    base = base.lower().strip()
    quote = quote.lower().strip()
    base_id = SYMBOL_ALIASES.get(base)
    quote_id = SYMBOL_ALIASES.get(quote)

    if base_id and quote in FIATS:
        rate = await get_rate(base_id, quote)
        result = amount * rate
        return result, f"{fmt(amount)} {base.upper()} = {fmt(result)} {quote.upper()}"

    if base in FIATS and quote_id:
        rate = await get_rate(quote_id, base)
        result = amount / rate
        return result, f"{fmt(amount)} {base.upper()} = {fmt(result)} {quote.upper()}"

    raise ValueError("пара должна быть вида «монета валюта», например: btc usd")