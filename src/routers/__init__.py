from fastapi import APIRouter

from src.routers import auth_router, profile_router

main_router = APIRouter()

main_router.include_router(auth_router.router)
main_router.include_router(profile_router.router)
