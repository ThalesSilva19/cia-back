from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.admin import router as admin_router
from src.routers.auth import router as auth_router
from src.routers.email import router as email_router
from src.routers.seat import router as seat_router
from src.settings import settings

app = FastAPI()

# CORS origins carregadas das configurações
origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(seat_router)
app.include_router(email_router)
