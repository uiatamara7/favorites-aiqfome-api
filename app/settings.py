# Esse arquivo contém as configuraçoes

from pydantic_settings import BaseSettings
from typing import List

# Classe principal para a configuração:
class Settings(BaseSettings):
    # Básico
    app_name: str = "API Produtos Favoritos"
    database_url: str 

    # CORS
    cors_origins: List[str] = ["*"] # Neste caso todas as origens são permitidas, mas na produção podemos mudar para domínios seguros
    
    # Auth
    api_key: str | None = None

    # Integrações externas
    fakestore_base_url: str = "https://fakestoreapi.com"
    http_timeout_seconds: float = 5.0

    class Config:
        env_file = ".env"

settings = Settings()
