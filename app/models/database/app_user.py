from sqlmodel import Field, SQLModel

class AppUser(SQLModel, table=True):
    user_id: str = Field(primary_key=True)
    username: str
    email: str
    password: str
