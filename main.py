from fastapi import FastAPI, WebSocket, Depends
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from core.models import Line, Train, Base
from core.database import db_helper
import uvicorn


async def lifespan(app: FastAPI) -> None:
    async with db_helper.engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


@app.get("/")
def index():
    return {"status": "Success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
