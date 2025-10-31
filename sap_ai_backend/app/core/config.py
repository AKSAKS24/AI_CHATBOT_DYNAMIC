from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    log_level: str
    sap_base_url: str
    sap_username: str
    sap_password: str

    openai_api_key: str
    model_name: str = "gpt-4-turbo"

    port: int
    host: str

    class Config:
        env_file = ".env"

settings = Settings()