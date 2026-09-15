import aiohttp

from bot.clients.api_client import ApiClient


class FakeResponse:
    def __init__(self, status: int, payload: dict):
        self.status = status
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method: str, url: str, json: dict | None = None):
        self.calls.append((method, url, json))
        return self.response


async def test_api_client_accepts_created_response():
    session = FakeSession(FakeResponse(201, {"id": 1}))
    client = ApiClient(session)

    result = await client._request("POST", "http://api/test", json={"value": 1})

    assert result == ({"id": 1}, "ok")
    assert session.calls == [("POST", "http://api/test", {"value": 1})]


async def test_api_client_maps_blocked_response():
    session = FakeSession(FakeResponse(403, {}))
    client = ApiClient(session)

    result = await client._request("GET", "http://api/test")

    assert result == (None, "blocked")


async def test_api_client_maps_network_failure():
    class FailingSession:
        def request(self, *args, **kwargs):
            del args, kwargs
            raise aiohttp.ClientConnectionError("connection failed")

    client = ApiClient(FailingSession())

    result = await client._request("GET", "http://api/test")

    assert result == (None, "unavailable")


async def test_api_client_maps_request_limit_conflict():
    session = FakeSession(FakeResponse(409, {}))
    client = ApiClient(session)

    result = await client.create_request(1, {"service_name": "Сайт"})

    assert result == (None, "limit")


async def test_api_client_returns_empty_payload_for_empty_success():
    session = FakeSession(FakeResponse(204, {}))
    client = ApiClient(session)

    result = await client._request("DELETE", "http://api/test")

    assert result == (None, "ok")
