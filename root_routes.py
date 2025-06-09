from fastapi import APIRouter


from models import *



router = APIRouter()

@router.get("/")
async def index():
    return {
        "status":"api works"
    }
