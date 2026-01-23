from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel
from starlette.responses import JSONResponse

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # 1. Get the first error from the list
    error = exc.errors()[0]

    # 2. Extract the message and clean the Pydantic prefix
    msg = error.get("msg").replace("Value error, ", "")

    # 3. Return the exact flat format you requested
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": msg},
    )
app.include_router(router)