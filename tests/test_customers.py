# Neste arquivo tem um teste automatizado para validar o CRUD para rota /v1/customers

from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.settings import settings
from app.db import SessionLocal
import app.models as models

# Cria o cliente HTTP e define o cabeçalho
client = TestClient(app)
API = {"x-api-key": settings.api_key}

# Teste que vai cobrir o ciclo de vida do cliente
def test_customers_crud():
    # Criando um cliente fictício no banco
    r = client.post("/v1/customers", headers=API, json={"name": "Maria", "email": "maria@example.com"})
    assert r.status_code == 201
    cid = r.json()["id"]

    # Verificando se o cliente fictício criado pode ser buscado com sucesso
    r = client.get(f"/v1/customers/{cid}", headers=API)
    assert r.status_code == 200
    assert r.json()["email"] == "maria@example.com"

    # Listando os clientes cadastrados e confirma se o ID do cliente criado está presente na lista
    r = client.get("/v1/customers?page=1&page_size=10", headers=API)
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())

    # Atualizando o nome do cliente
    r = client.put(f"/v1/customers/{cid}", headers=API, json={"name": "Mariana"})
    assert r.status_code == 200
    assert r.json()["name"] == "Mariana"

    # Tentando criar outro cliente com o mesmo e-mail
    r2 = client.post("/v1/customers", headers=API, json={"name": "Mariaa", "email": "maria@example.com"})
    assert r2.status_code == 409

    # Deletando o cliente
    r = client.delete(f"/v1/customers/{cid}", headers=API)
    assert r.status_code == 204

    # Verificando se o cliente realmente foi removido do banco
    r = client.get(f"/v1/customers/{cid}", headers=API)
    assert r.status_code == 404
