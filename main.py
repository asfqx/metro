from fastapi import FastAPI

import uvicorn

from api import router as api_router

from core.database.database import setup_database


async def lifespan(app: FastAPI) -> None:
    await setup_database()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
def index():
    return {"status": "Success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
