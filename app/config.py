from pydantic import BaseSettings

# TODO Create a .env file and read these values from there
class Settings(BaseSettings):
    database_dsn: str = "sqlite+aiosqlite:///app/moneytoring.db"
    test_database_dsn: str = "sqlite+aiosqlite:///app/test.db"
    oauth2_secret_key: str = "f2f65a472fd0632f2ae77bce52ab45c97ec8a598ce67d0cb2e145db5daa429f4"
    oauth2_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    nordigen_base_url: str = "https://ob.nordigen.com/api/v2"
    nordigen_key: str = "70d1bb9cbd0cfeb71532bb8649b563c4cf2a9aa11cb0bed5f4a33993f3f8be20b7db438dc75bf44683a4923b2856adfc58a81538e67c226d773c50000019ecb3" 
    nordigen_id: str = "6b608a17-7884-40ec-8eae-03b49ee5b50e" 
