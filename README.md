# Projeto: API de Produtos Favoritos para o aiqfome

## 📅 Contexto
Criei essa API para atender a este contexto:
> Este foi um desafio para a vaga de dev backend no aiqfome (Magalu)

O aiqfome está expandindo seus canais de integração e precisa de uma API robusta para gerenciar os "produtos favoritos" de usuários na plataforma.
Essa funcionalidade será usada por apps e interfaces web para armazenar e consultar produtos marcados como favoritos pelos clientes. A API terá alto volume de uso e integrará com outros sistemas internos e externos.





## 🚀 Tecnologias Utilizadas

| Categoria | Tecnologias |
|------------|-------------|
| **Linguagem** | Python 3.12 |
| **Framework Web** | FastAPI |
| **Banco de Dados** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 |
| **Cliente HTTP** | HTTPX |
| **Testes** | Pytest + Respx |
| **Variáveis de Ambiente** | Pydantic Settings |
| **Infraestrutura** | Docker |



## 🧱 Estrutura do Projeto

```bash
magalu-test/
├── app/
│   ├── main.py              # Ponto de entrada da API
│   ├── db.py                # Conexão com o banco de dados
│   ├── models.py            # Modelos ORM (tabelas)
│   ├── schemas.py           # Schemas Pydantic (validação e resposta)
│   ├── integrations/
│   │   └── fakestore.py     # Integração externa com FakeStore API
│   └── settings.py          # Configurações e variáveis de ambiente
├── tests/                   # Todos os testes automatizados
│   ├── test_customers.py
│   ├── test_favorites.py
│   └── test_health.py
├── .env.example
├── requirements.txt
└── README.md
```


## ⚙️ Configuração do Ambiente

### 🔹 1. Clonar o repositório

```bash
git clone https://github.com/uiatamara7/favorites-aiqfome-api.git
cd favorites-aiqfome-api
```

### 🔹 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
```

### 🔹 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 🔹 4. Configurar variáveis de ambiente
Crie um arquivo .env na raiz do projeto com base no .env.example:

```bash
cp .env.example .env
```

## 🐘 Subindo o Banco de Dados com Docker
Para rodar o banco localmente, siga esse exemplo:

```bash
sudo docker run --name pg-favorites \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=favorites \
  -p 5432:5432 -d postgres:16
```

## 🚀 Executando a API

```bash
uvicorn app.main:app --reload
```

## 🔐 Autenticação via API Key

Devido o tempo, essa foi a forma de autenticação simples que consegui fazer para entregar o projeto no prazo.

Todos os endpoints requerem o header:

```bash
x-api-key: favorites-myapi
```
> A chave pode ser configurada no .env.

## 🧪 Rodando os Testes Automatizados
Os testes cobrem:

* CRUD de clientes
* Integração com FakeStore API
* Gerenciamento de favoritos
* Health check da aplicação

```bash
pytest -v
```

## 🧩 Exemplos de Requisições

### ➕ Criar Cliente
```bash
curl -X POST http://localhost:8000/v1/customers \
  -H "Content-Type: application/json" \
  -H "x-api-key: favorites-myapi" \
  -d '{"name": "Maria", "email": "maria@example.com"}'
```

### ❤️ Adicionar Produto Favorito
```bash
curl -X POST http://localhost:8000/v1/customers/1/favorites \
  -H "x-api-key: favorites-myapi" \
  -d '{"product_id": 3}'
```

### 📦 Buscar Favoritos
```bash
curl -X GET http://localhost:8000/v1/customers/1/favorites \
  -H "x-api-key: favorites-myapi"
```

## ⭐ Minhas considerações sobre o projeto
Acredito que foi um desafio bem legal para mostrar meus conhecimentos! Tive alguns imprevisto nesta semana, mas acredito que se houvesse mais tempo, eu poderia me dedicar melhor à autenticação e autorização, tornar uma API pública mais robusta. Mas consegui entregar boa parte dos requisitos:

* Desenvolva uma API RESTful (Estruture bem o código, seguindo boas práticas REST)
* Criar, visualizar, editar e remover clientes
* Dados obrigatórios: nome e e-mail
* Um mesmo e-mail não pode se repetir no cadastro
* Um cliente deve ter uma lista de produtos favoritos
* Os produtos devem ser validados via API externa (Fakestore)
* Um produto não pode ser duplicado na lista de um cliente
* Produtos favoritos devem exibir: ID, título, imagem, preço e review
* Evite duplicidade de dados
* Usei linguagem Python e PostgreSQL

Ainda vejo que entregue a mais criar testes e usei docker.

Obrigada :) 
