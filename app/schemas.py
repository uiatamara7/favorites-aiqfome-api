# Esse arquivo terá os modelos de dados

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# Classe para criar um novo cliente
class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

# Classe para editar um cliente existente
class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None

# Classe para remover um cliente
class CustomerOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        from_attributes = True

# Classe para adicionar um produto aos favoritos
class FavoriteCreate(BaseModel):
    product_id: int = Field(gt=0)

# Classe para exibir os produtos favoritos
class FavoriteProductOut(BaseModel):
    id: int
    title: str
    image: Optional[str] = None
    price: float
    review: Optional[float] = None