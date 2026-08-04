from fastapi import FastAPI

from core.config import get_settings
from core.exceptions import registrar_exception_handlers
from core.logging import configurar_logging
from presentation.api.middleware import RequestIDMiddleware
from presentation.api.routers import api_router


def create_app() -> FastAPI:
    settings = get_settings()
    configurar_logging(settings.log_level)

    app = FastAPI(
        title="MPI — Personalização Inteligente de Materiais Didáticos",
        version="0.1.0",
    )
    app.add_middleware(RequestIDMiddleware)
    registrar_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
