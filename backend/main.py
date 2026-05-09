from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api_router import api_router
from auth.grafana.service import GrafanaTokenRefreshService
from auth.grafana.init import init as init_grafana

ORIGIN = ["http://localhost:3000"]

token_manager = GrafanaTokenRefreshService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_grafana(token_manager)
    token_manager.start_token_refresh_loop()
    try:
        yield
    finally:
        token_manager.stop_token_refresh_loop()



app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
