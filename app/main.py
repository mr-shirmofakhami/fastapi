from fastapi import FastAPI
from app.core import database
from app.models import user
from app.routers import user as user_router
from app.routers import auth as auth_router


# Create tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FastAPI + PostgreSQL App")

# ✅ Root (home) endpoint
@app.get("/")
def read_root():
    return {"message": "🚀 FastAPI is running! Try /docs to see the API"}

# Include routers
app.include_router(auth_router.router)
app.include_router(user_router.router)