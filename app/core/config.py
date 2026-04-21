from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EazyBill"
    debug: bool = True
    database_url: str = ""
    test_database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 525960

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
