from app.models.request_model import Request, StatusEnum
from app.models.user_model import User
from config import settings


async def test_paginated_requests_returns_envelope_with_correct_page(client):
    test_client, session_factory = client
    async with session_factory() as session:
        user = User(tg_user_id=42)
        session.add(user)
        await session.flush()
        session.add_all(
            [
                Request(
                    service_name=f"Услуга {i}",
                    phone_number=f"+400000000{i}",
                    user_id=user.id,
                    status=StatusEnum.NEW,
                )
                for i in range(3)
            ]
        )
        await session.commit()

    response = test_client.get(
        "/requests/paginated",
        params={"page": 1, "page_size": 2},
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2


async def test_paginated_requests_requires_authorization(client):
    test_client, session_factory = client
    response = test_client.get("/requests/paginated")

    assert response.status_code == 401


async def test_paginated_requests_rejects_invalid_page_size(client):
    test_client, session_factory = client
    response = test_client.get(
        "/requests/paginated",
        params={"page": 1, "page_size": 1000},
        headers={"X-Service-Token": settings.SERVICE_TOKEN},
    )

    assert response.status_code == 422
