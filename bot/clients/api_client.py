import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, TypeVar

import aiohttp

from config import settings
from bot.dtos import (
    AdminData,
    CanCreateRequestData,
    RequestCreateData,
    RequestData,
    UserData,
)

API_URL = settings.API_URL

T = TypeVar("T")


def _handle_api_errors(
    func: Callable[..., Awaitable[tuple[T | None, str]]],
) -> Callable[..., Awaitable[tuple[T | None, str]]]:
    """Декоратор для единообразной обработки ошибок HTTP-запросов."""
    async def wrapper(*args: Any, **kwargs: Any) -> tuple[T | None, str]:
        try:
            return await func(*args, **kwargs)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return None, "unavailable"  # type: ignore[return-value]
    return wrapper


class ApiClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @_handle_api_errors
    async def _request(
        self,
        method: str,
        url: str,
        json: dict | None = None,
    ) -> tuple[Any | None, str]:
        async with self.session.request(method, url, json=json) as response:
            if 200 <= response.status < 300:
                if response.status == 204:
                    return None, "ok"
                return await response.json(), "ok"
            return None, self._status_to_code(response.status)

    @staticmethod
    def _status_to_code(status: int) -> str:
        mapping = {
            403: "blocked",
            404: "not_found",
            409: "conflict",
            422: "validation_error",
        }
        return mapping.get(status, "server_error")

    async def get_user(self, telegram_id: int) -> tuple[UserData | None, str]:
        result, status = await self._request(
            "GET",
            f"{API_URL}/users/by-telegram/{telegram_id}",
        )
        return UserData.model_validate(result) if result is not None else None, status

    async def create_user(
        self,
        telegram_id: int,
        username: str | None,
    ) -> tuple[UserData | None, str]:
        result, status = await self._request(
            "POST",
            f"{API_URL}/users/",
            json={"tg_user_id": telegram_id, "username": username},
        )
        return UserData.model_validate(result) if result is not None else None, status

    async def can_create_request(self, telegram_id: int) -> CanCreateRequestData:
        result, status = await self._request(
            "GET",
            f"{API_URL}/users/by-telegram/{telegram_id}/can-create-request",
        )
        if status == "ok" and result is not None:
            return CanCreateRequestData.model_validate(result)
        if status == "not_found":
            return CanCreateRequestData(allowed=False, error="not_found")
        return CanCreateRequestData(allowed=False, error="server_error")

    async def create_request(
        self,
        telegram_id: int,
        data: RequestCreateData | Mapping[str, str],
    ) -> tuple[RequestData | None, str]:
        result, status = await self._request(
            "POST",
            f"{API_URL}/requests/{telegram_id}",
            json=(
                data.model_dump()
                if isinstance(data, RequestCreateData)
                else dict(data)
            ),
        )
        if status == "ok":
            return RequestData.model_validate(result) if result is not None else None, "ok"
        status_map = {
            "conflict": "limit",
        }
        return None, status_map.get(status, status)

    async def get_active_admins(self) -> tuple[list[AdminData] | None, str]:
        result, status = await self._request("GET", f"{API_URL}/admins/active")
        return (
            [AdminData.model_validate(item) for item in result]
            if result is not None
            else None
        ), status

    async def get_request(self, request_id: int) -> tuple[RequestData | None, str]:
        result, status = await self._request("GET", f"{API_URL}/requests/{request_id}")
        return RequestData.model_validate(result) if result is not None else None, status

    async def update_request_status(
        self,
        request_id: int,
        status: str,
    ) -> tuple[RequestData | None, str]:
        result, response_status = await self._request(
            "PUT",
            f"{API_URL}/requests/{request_id}",
            json={"status": status},
        )
        return (
            RequestData.model_validate(result) if result is not None else None
        ), response_status

    async def get_requests(self) -> tuple[list[RequestData] | None, str]:
        result, status = await self._request("GET", f"{API_URL}/requests/")
        return (
            [RequestData.model_validate(item) for item in result]
            if result is not None
            else None
        ), status

    async def get_user_requests(
        self,
        telegram_id: int,
    ) -> tuple[list[RequestData] | None, str]:
        result, status = await self._request(
            "GET",
            f"{API_URL}/requests/by-telegram/{telegram_id}",
        )
        return (
            [RequestData.model_validate(item) for item in result]
            if result is not None
            else None
        ), status
