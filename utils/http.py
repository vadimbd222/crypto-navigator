import asyncio
import logging

import aiohttp

from config import PROXY_URL

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Внешний API недоступен или вернул ошибку."""


async def fetch_json(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    retries: int = 3,
) -> dict:
    """GET-запрос к внешнему API с повторными попытками.

    Делает до retries попыток с паузой между ними.
    Возвращает JSON-ответ, при неудаче поднимает ServiceError.
    """
    # Если в .env задан прокси — запросы к API идут через него,
    # так же как и запросы к Telegram. На сервере прокси пустой.
    request_kwargs: dict = {}
    if PROXY_URL:
        request_kwargs["proxy"] = PROXY_URL

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    url, params=params, headers=headers, **request_kwargs
                ) as resp:
                    if resp.status != 200:
                        raise ServiceError(f"статус {resp.status}")
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ServiceError) as exc:
            last_exc = exc
            logger.warning(
                "Попытка %s/%s к %s не удалась: %s",
                attempt, retries, url, exc,
            )
            if attempt < retries:
                await asyncio.sleep(1.5 * attempt)
    raise ServiceError(f"API недоступен ({last_exc})")