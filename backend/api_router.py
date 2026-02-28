from fastapi import APIRouter

from vaultpadlock.routes import router as vault_padlock_router

api_router = APIRouter()
api_router.include_router(prefix="/vaultpadlock", router=vault_padlock_router)
