# app/main.py

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from api.v1.router import router
from db.session import lifespan

description = """Seedless Flavors API for website and mobile app.\n
[Website](https://www.seedlessflavors.com) | 
[Youtube Channel](https://www.youtube.com/@SeedlessFlavors/featured) | 
[X](https://x.com/SeedlessFlavors) | 
[Instagram](https://www.instagram.com/seedlessflavors)
"""

app = FastAPI(
    title="Seedless Flavors API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Cihat Ertem",
        "url": "https://cihatertem.dev",
        "email": "cihatertem+seedlessflavors@gmail.com",
    },
    license_info={
        "name": "GNU GENERAL PUBLIC LICENSE Version 3",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html",
    },
    lifespan=lifespan,
)

app.include_router(router)


@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(
        request: Request, exc: IntegrityError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Oops! {exc.__class__.__name__} error!"},
    )


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "healthy"})
