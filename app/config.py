# Database config variables
DATABASE_URL = f"sqlite+aiosqlite:///app/moneytoring.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///app/test.db"

# OAuth2 config variables
SECRET_KEY = "f2f65a472fd0632f2ae77bce52ab45c97ec8a598ce67d0cb2e145db5daa429f4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120