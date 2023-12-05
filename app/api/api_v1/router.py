from fastapi import APIRouter

from .endpoints import category

router = APIRouter(prefix="/api_v1", tags=["api_v1"])

router.include_router(category.router)
