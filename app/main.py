from fastapi import FastAPI

from app.routers import auth
from app.routers import institution
from app.routers import requisition

app = FastAPI()

app.include_router(auth.router)
app.include_router(institution.router)
app.include_router(requisition.router)
