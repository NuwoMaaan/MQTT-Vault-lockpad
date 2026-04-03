from fastapi import APIRouter

from vaultpadlock.routes import router as vault_padlock_router
from ble.routes import router as ble_router
from auth.routes import router as auth_router

api_router = APIRouter()
api_router.include_router(prefix="/vaultpadlock", router=vault_padlock_router, tags=['Vault Padlock'])
api_router.include_router(prefix="/ble", router=ble_router, tags=['BLE'])
api_router.include_router(prefix="/auth", router=auth_router, tags=['Authentication'])

