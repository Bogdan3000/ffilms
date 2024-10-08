"""Basic wrapper for all http requests of the package"""
from typing import Any, Optional, TypedDict

import httpx

__all__ = ('get_response', 'DEFAULT_CLIENT', 'DEFAULT_REQUEST_KWARGS')


class RequestKwargs(TypedDict):
    content: Optional[Any]
    data: Optional[Any]
    files: Optional[Any]
    json: Optional[Any]
    params: Optional[Any]
    headers: Optional[Any]
    cookies: Optional[Any]
    auth: Optional[Any]
    follow_redirects: Optional[bool | Any]
    timeout: Optional[Any]
    extensions: Optional[Any]


DEFAULT_CLIENT = httpx.AsyncClient(headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0', "Origin": "https://rezka.ag", "Referer": "https://rezka.ag/", "Sec-Ch-Ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"'}, follow_redirects=True)
DEFAULT_REQUEST_KWARGS: RequestKwargs | dict = {}


async def get_response(method: str, url: str, **kwargs) -> httpx.Response:
    """
    passed **kwargs have more weight than DEFAULT_REQUEST_KWARGS.
    Returns DEFAULT_CLIENT.request(method, url, **kwargs, **DEFAULT_REQUEST_KWARGS)
    """
    for k, v in DEFAULT_REQUEST_KWARGS.items():
        if k not in kwargs:
            kwargs[k] = v
    return await DEFAULT_CLIENT.request(method, url, **kwargs)
