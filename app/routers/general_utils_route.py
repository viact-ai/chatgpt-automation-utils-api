from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def general_utils_info():
    return {
        "message": "General Utilities API",
    }
