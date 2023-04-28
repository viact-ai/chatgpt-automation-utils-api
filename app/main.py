from os import getenv

import dotenv
from db import db_helper
from fastapi import FastAPI
from routers import crawler_route, general_utils_route, llm_route

dotenv.load_dotenv()

assert getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY not set in .env"

app = FastAPI()


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
