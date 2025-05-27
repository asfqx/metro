from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "1"
    db_name: str = "metro"
    db_host: str = "localhost"
    db_port: int = 5433
    db_url: str = (
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )


settings = Settings()
