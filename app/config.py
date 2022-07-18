from pydantic import BaseSettings

# TODO Create a .env file and read these values from there
class Settings(BaseSettings):
    database_dsn: str = "sqlite+aiosqlite:///app/moneytoring.db"
    test_database_dsn: str = "sqlite+aiosqlite:///app/test.db"
    oauth2_secret_key: str = "f2f65a472fd0632f2ae77bce52ab45c97ec8a598ce67d0cb2e145db5daa429f4"
    oauth2_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
