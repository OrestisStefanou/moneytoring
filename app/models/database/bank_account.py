from sqlmodel import Field, SQLModel


class BankAccount(SQLModel, table=True):
    account_id: str = Field(primary_key=True)
    requisition_id:str = Field(foreign_key="requisition.id")
    name: str
    currency: str
