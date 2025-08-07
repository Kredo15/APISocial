from fastapi import APIRouter

from src.routers import auth, profile

main_router = APIRouter()

main_router.include_router(auth.router)
main_router.include_router(profile.router)
