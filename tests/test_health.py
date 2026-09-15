from app.routes.health_routes import get_health


def test_health_route_returns_ok():
    response = get_health()

    assert response.status_code == 200
    assert response.body == b'{"status":"ok"}'
