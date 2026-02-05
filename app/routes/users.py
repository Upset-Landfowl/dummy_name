
from app import models, schemas
from app.dependencies import get_db
from app.utils import utils
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/create-account", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        password=hashed_password)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="If email is valid, instructions have been sent. Check your email")
    return {"detail": "If email is valid, instructions have been sent. Check your email"}

    
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    result = db.get(models.User, id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return result