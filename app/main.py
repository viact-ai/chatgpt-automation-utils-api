from os import getenv

import dotenv
from fastapi import FastAPI
from routers import general_utils_route

dotenv.load_dotenv()

assert getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY not set in .env"

app = FastAPI()


app.include_router(
    general_utils_route.router,
    prefix="/general_utils",
)


@app.get("/")
def root():
    return {
        "message": "ChatGPT Automation API",
    }
