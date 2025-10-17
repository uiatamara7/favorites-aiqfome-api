# Esse arquivo terá as tabelas do banco

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from .db import Base

# Cria a tabela "Customer" com suas colunas
class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("email", name="uq_customer_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="customer", cascade="all, delete-orphan"
    )

# Cria a tabela "Favorites" e a relação com "Customer" 
class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("customer_id", "product_id", name="uq_customer_product"),)
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="favorites")

    # Isso garante que o mesmo cliente não possa favoritar o mesmo produto duas vezes
    __table_args__ = (UniqueConstraint("customer_id", "product_id", name="uq_customer_product"),)