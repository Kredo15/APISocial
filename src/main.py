import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.config.settings import settings
from src.auth.routers.login_handlers import router as auth_router
from src.auth.routers.user_handlers import router as user_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
