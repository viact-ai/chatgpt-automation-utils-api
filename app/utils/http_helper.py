from typing import Any, Coroutine

import httpx


async def async_request(
    url: str,
    headers: dict = None,
    params: dict = None,
    timout: int = 30,
) -> Coroutine[Any, Any, httpx.Response]:
    async with httpx.AsyncClient() as client:
        return await client.get(
            url,
            headers=headers,
            params=params,
            timeout=timout,
        )
