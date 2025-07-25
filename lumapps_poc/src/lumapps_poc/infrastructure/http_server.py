from fastapi import FastAPI

from lumapps_poc.adapters import endpoints


def create_app() -> FastAPI:
    app = FastAPI(redoc_url="/redoc")
    app.include_router(endpoints.router)
    return app