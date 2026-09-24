from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "payment-service"
    database_url: str = "postgresql+psycopg://agent:agent@127.0.0.1:55432/payments"
    fraud_mock_url: str = "http://127.0.0.1:8010"
    otel_exporter_otlp_endpoint: str = "http://127.0.0.1:4317"
    deployment_environment: str = "local"


settings = Settings()
