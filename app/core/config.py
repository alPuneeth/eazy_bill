from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EazyBill"
    debug: bool = True
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 525960

    class Config:
        env_file = ".env"


settings = Settings()
