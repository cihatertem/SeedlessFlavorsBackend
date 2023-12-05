# app/main.py

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from api.api_v1.router import router
from db.session import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(
        request: Request, exc: IntegrityError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"Oops! {exc.__class__.__name__}. {exc.params} is "
                       f"already exist!"
        },
    )


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "healthy"})
