# FastAPI Project

A FastAPI + PostgreSQL backend with JWT authentication, refresh tokens, and role-based access control (RBAC).

## 🚀 Features
- JWT-based authentication
- Refresh token mechanism (stored in PostgreSQL)
- Role-based routes (Admin, User)
- Owner or Admin restrictions
- Alembic migrations
- PostgreSQL database integration

---

## 📦 Installation
```bash
git clone https://github.com/mr-shirmofakhami/fastapi.git
cd fastapi
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt 

uvicorn app.main:app --reload --port 8001