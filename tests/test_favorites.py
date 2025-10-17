# Neste arquivo tem um teste automatizado para cobrir o fluxo completo de favoritos

import respx
from httpx import Response
from fastapi.testclient import TestClient
from app.main import app
from app.settings import settings

# Cria o cliente HTTP e define o cabeçalho
client = TestClient(app)
API = {"x-api-key": settings.api_key}

# Simula a resposta da FakeStore
def _mock_product(pid: int = 1):
    return {
        "id": pid,
        "title": "Test Product",
        "image": "http://img",
        "price": 19.9,
        "rating": {"rate": 4.7, "count": 100},
    }

def test_favorites_flow():
    # Criando cliente
    r = client.post("/v1/customers", headers=API, json={"name": "Maria", "email": "maria@example.com"})
    assert r.status_code == 201
    cid = r.json()["id"]

    base = settings.fakestore_base_url.rstrip("/")

    with respx.mock:
        respx.get(f"{base}/products/1").mock(return_value=Response(200, json=_mock_product(1)))

        # Add favorito
        r = client.post(f"/v1/customers/{cid}/favorites", headers=API, json={"product_id": 1})
        assert r.status_code == 201
        body = r.json()
        assert body["id"] == 1 and body["price"] == 19.9 and body["review"] == 4.7

        # Duplicado -> 409
        r = client.post(f"/v1/customers/{cid}/favorites", headers=API, json={"product_id": 1})
        assert r.status_code == 409

        # Listar
        r = client.get(f"/v1/customers/{cid}/favorites", headers=API)
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1 and items[0]["id"] == 1

        # Remover
        r = client.delete(f"/v1/customers/{cid}/favorites/1", headers=API)
        assert r.status_code == 204

        # Listar vazio
        r = client.get(f"/v1/customers/{cid}/favorites", headers=API)
        assert r.status_code == 200
        assert r.json() == []
