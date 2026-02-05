
from fastapi import APIRouter, status

router = APIRouter(
    prefix="",
    tags=["Root/Home"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "welcome to my api"}