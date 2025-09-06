from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import database
from .api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="Knowledge Extractor API",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
def root():
    return {"ok": True, "message": "See /docs for Swagger UI"}
