from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MQTT_BROKER: str 
    MQTT_PORT: int 
    MQTT_USERNAME: str 
    MQTT_PASSWORD: str 

settings = Settings()
