from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    API_KEY: str

    JWT_SECRET_KEY: str
    EXPIRE: int
    ALGORITHM: str = "HS256"

    GRAFANA_URL: str
    GRAFANA_DS_UID: str
    GRAFANA_USER: str
    GRAFANA_PASSWORD: str


settings = Settings()
