from os import getenv

import dotenv
from db import db_helper
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth_route,
    crawler_route,
    email_route,
    general_utils_route,
    llm_route,
)
from utils.config_utils import get_config

dotenv.load_dotenv()

assert getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY not set in .env"

config = get_config()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    general_utils_route.router,
    prefix="/general_utils",
)
app.include_router(
    crawler_route.router,
    prefix="/crawler",
)
app.include_router(
    llm_route.router,
    prefix="/llm",
)
app.include_router(
    email_route.router,
    prefix="/email",
)
app.include_router(
    auth_route.router,
    prefix="/auth",
)


# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(email_utils.send_scheduled_emails_loop())


@app.get("/")
def root():
    return {
        "message": "ChatGPT Automation API",
    }


@app.get("/test_db_connection")
def test_db_connection():
    client = db_helper.get_client()
    return {
        "message": "Connection successful"
        if db_helper.test_connection(client)
        else "Connection failed"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.app.host,
        port=config.app.port,
        workers=1,
    )
