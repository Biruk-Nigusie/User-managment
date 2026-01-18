from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from db.session import engine
from auth.router import router
app = FastAPI()
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
@asynccontextmanager
def on_startup():
    create_db_and_tables()
@app.get("/")
def root():
    return {"message": "Hello World"}
app.include_router(router)