from fastapi import APIRouter

from .endpoints import category, auth

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(category.router)
router.include_router(auth.router)
