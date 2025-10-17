# Esse arquivo é o ponto de entrada para criar a instância FastAPI

from fastapi import FastAPI, Depends, HTTPException, Header, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.settings import settings
from app.db import Base, engine, get_db
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut, FavoriteCreate, FavoriteProductOut
from app.integrations.fakestore import get_product_or_404
import app.models as models

# Criando a aplicação FastAPI
app = FastAPI()

# Configurando o CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Assim que a API subir ele vai criar as tabelas
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Auth simples por API Key
def require_api_key(x_api_key: str | None = Header(default=None)):
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="API key inválida")

# Endpoint simples de health check
@app.get("/health")
def health():
    return {"status": "ok"}


# A partir daqui vem o CRUD dos clientes

# Endpoint para criar cliente
@app.post("/v1/customers", response_model=CustomerOut, status_code=201,
          dependencies=[Depends(require_api_key)])
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    # Aqui garante que um mesmo e-mail não pode se repetir no cadastro
    exists = db.execute(select(models.Customer).where(models.Customer.email == payload.email)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    obj = models.Customer(name=payload.name, email=payload.email)
    db.add(obj)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    
    db.refresh(obj)
    return obj

# Endpoint para buscar cliente específico
@app.get("/v1/customers/{customer_id}", response_model=CustomerOut,
         dependencies=[Depends(require_api_key)])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Customer, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return obj

# Endpoint para listar todos os clientes
@app.get("/v1/customers", response_model=list[CustomerOut],
         dependencies=[Depends(require_api_key)])
def list_customers(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    offset = (page - 1) * page_size
    stmt = select(models.Customer).order_by(models.Customer.id.asc()).offset(offset).limit(page_size)
    return db.execute(stmt).scalars().all()

# Endpoint para atualizar cliente existente
@app.put("/v1/customers/{customer_id}", response_model=CustomerOut,
         dependencies=[Depends(require_api_key)])
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Customer, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Se for trocar e-mail, validar unicidade
    if payload.email and payload.email != obj.email:
        exists = db.execute(select(models.Customer).where(models.Customer.email == payload.email)).scalar_one_or_none()
        if exists:
            raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    if payload.name is not None:
        obj.name = payload.name
    if payload.email is not None:
        obj.email = payload.email

    db.commit()
    db.refresh(obj)
    return obj

# Endpoint para remover cliente
@app.delete("/v1/customers/{customer_id}", status_code=204,
            dependencies=[Depends(require_api_key)])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Customer, customer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(obj)
    db.commit()
    return

# Endpoint para adicionar um produto aos favoritos
@app.post(
    "/v1/customers/{customer_id}/favorites",
    response_model=FavoriteProductOut,
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def add_favorite(
    customer_id: int = Path(gt=0),
    payload: FavoriteCreate = ...,
    db: Session = Depends(get_db),
):
    # Verifica se o cliente existe no banco
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Valida produto na FakeStore
    prod = get_product_or_404(payload.product_id)

    # Impede que um cliente favorite o mesmo produto duas vezes
    exists = db.execute(
        select(models.Favorite).where(
            and_(
                models.Favorite.customer_id == customer_id,
                models.Favorite.product_id == payload.product_id,
            )
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Produto já favoritado para este cliente")
    
    # Cria registro no banco e retorna os dados do produto
    fav = models.Favorite(customer_id=customer_id, product_id=payload.product_id)
    db.add(fav)
    db.commit()
    return prod

# Endpoint para listar os produtos favoritos do cliente
@app.get(
    "/v1/customers/{customer_id}/favorites",
    response_model=list[FavoriteProductOut],
    dependencies=[Depends(require_api_key)],
)
def list_favorites(customer_id: int = Path(gt=0), db: Session = Depends(get_db)):
    # Verifica se o cliente existe
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Busca todos os registros de favoritos no banco
    stmt = select(models.Favorite).where(models.Favorite.customer_id == customer_id).order_by(models.Favorite.id.asc())
    favs = db.execute(stmt).scalars().all()

    # Para cada favorito, com dados da FakeStore, adiciona título, imagem, preço e review
    # (simples: N chamadas HTTP; dá pra otimizar depois com cache/batch)
    products: list[FavoriteProductOut] = []
    for f in favs:
        products.append(FavoriteProductOut(**get_product_or_404(f.product_id)))
    return products

# Endpoint para remove um produto da lista de favoritos
@app.delete(
    "/v1/customers/{customer_id}/favorites/{product_id}",
    status_code=204,
    dependencies=[Depends(require_api_key)],
)
def delete_favorite(
    customer_id: int = Path(gt=0),
    product_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    # Verifica se o cliente existe
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Busca o favorito específico e deleta
    stmt = select(models.Favorite).where(
        and_(models.Favorite.customer_id == customer_id, models.Favorite.product_id == product_id)
    )
    fav = db.execute(stmt).scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    db.delete(fav)
    db.commit()
    return

