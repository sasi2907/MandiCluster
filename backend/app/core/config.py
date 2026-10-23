from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "MandiCluster API"
    app_description: str = (
        "Explore unsupervised market-price clusters "
        "for Indian agricultural commodities."
    )
    app_version: str = "1.0.0"

    frontend_origin: str = "http://localhost:5173"

    db_user: str = "postgres"
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "mandicluster_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()
