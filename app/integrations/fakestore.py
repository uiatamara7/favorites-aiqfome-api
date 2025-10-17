# Nesse arquivo tem o módulo de integração com a FakeStore API

import httpx
from fastapi import HTTPException
from app.settings import settings

# Cliente HTTP
_client = httpx.Client(timeout=settings.http_timeout_seconds)

# Mapeamento e limpeza dos dados para manter o padrão 
def _map_product(p: dict) -> dict:
    rating = p.get("rating") or {}
    return {
        "id": p["id"],
        "title": p["title"],
        "image": p.get("image"),
        "price": float(p["price"]),
        "review": float(rating["rate"]) if "rate" in rating else None,
    }

# GET e erros
def get_product_or_404(product_id: int) -> dict:
    url = f"{settings.fakestore_base_url}/products/{product_id}"
    try:
        r = _client.get(url)
    except httpx.HTTPError:
        # erro de rede/time-out
        raise HTTPException(status_code=502, detail="Erro ao consultar produto externo")
    if r.status_code == 404:
        raise HTTPException(status_code=400, detail="Produto inválido (não encontrado na FakeStore)")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Falha na integração com FakeStore")
    data = r.json()
    # FakeStore retorna objeto vazio em alguns casos edge — valide id
    if not data or "id" not in data:
        raise HTTPException(status_code=400, detail="Produto inválido")
    return _map_product(data)
