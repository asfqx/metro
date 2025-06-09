from fastapi import APIRouter
from starlette.websockets import WebSocket
from sqlalchemy import select
from api.train.crud import get_trains
from httpx import AsyncClient
import json

router = APIRouter()


@router.get("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        request = await websocket.receive_json()
        if request["action"] == "get_data":
            update_data = await update()
            await websocket.send_json(update_data)
        elif request["action"] == "update_data":
            received_data = json.loads(request["data"])


async def update():
    async with AsyncClient() as client:
        data = await client.get("http://127.0.0.1:8081/api")
        return data.json()
