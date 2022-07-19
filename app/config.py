from pydantic import BaseSettings

# TODO Create a .env file and read these values from there
class Settings(BaseSettings):
    database_dsn: str = "sqlite+aiosqlite:///app/moneytoring.db"
    test_database_dsn: str = "sqlite+aiosqlite:///app/test.db"
    oauth2_secret_key: str = "f2f65a472fd0632f2ae77bce52ab45c97ec8a598ce67d0cb2e145db5daa429f4"
    oauth2_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    nordigen_base_url: str = "https://ob.nordigen.com/api/v2"
    nordigen_key: str = "f0af3ec394b363949090ae58e916d13beafbafd8b9da15db545cafd14ee4c0449ed64f8db6e01f9fe0bb715746a1c5c8c70f4cc2627871da410fd153665aa28b" 
    nordigen_id: str = "08bbe997-fa27-47cb-95d0-779ee8a364da" 
