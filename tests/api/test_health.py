from fastapi.testclient import TestClient

from core.config import Settings, get_settings
from presentation.api.main import app


def test_health_retorna_200_e_status_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "development"}


def test_health_propaga_request_id_na_resposta() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={"X-Request-ID": "meu-id-de-teste"})

    assert response.headers["X-Request-ID"] == "meu-id-de-teste"


def test_health_reflete_settings_injetada_via_dependency_override() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(environment="production")
    try:
        response = TestClient(app).get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.json()["environment"] == "production"
