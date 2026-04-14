from enum import StrEnum

class Scope(StrEnum):
    BLE_READ = "ble:read"
    BLE_WRITE = "ble:write"
    VAULT_METRICS_READ = "vault:metrics:read"
    VAULT_STATUS_READ = "vault:status:read"
    VAULT_EVENTS_READ = "vault:events:read"

class BleScopes:
    READ = Scope.BLE_READ
    WRITE = Scope.BLE_WRITE

class VaultScopes:
    METRICS_READ = Scope.VAULT_METRICS_READ
    STATUS_READ = Scope.VAULT_STATUS_READ
    EVENTS_READ = Scope.VAULT_EVENTS_READ