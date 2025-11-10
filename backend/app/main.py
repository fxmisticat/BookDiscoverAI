from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import router as api_router
from .config import get_settings
from .database import create_db_and_tables
from .services.log_service import record_log


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="BookDiscoverAI API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        create_db_and_tables()
        record_log("INFO", "BookDiscoverAI backend started")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")

    return app


app = create_application()
