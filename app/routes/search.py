from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session
from app import models, schemas

from app.dependencies import get_db
from app.utils import jwt


router = APIRouter(prefix="/search",
                   tags=["Search"])

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.PostResponse])
def search(params: schemas.QueryParams = Depends(), current_user: models.User = Depends(jwt.get_current_user), 
           db: Session = Depends(get_db)):
    if not params.q or not params.q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enter a valid search term.")
    stmt = (select(models.Post.id, 
                models.Post.title, 
                models.Post.content, 
                models.Post.published,
                models.Post.rating, 
                models.Post.created_at,
                models.User.email.label("created_by"),
                func.count(models.Vote.post_id).label("votes"))
                .join(models.User, models.Post.user_id == models.User.id, isouter=True)
                .outerjoin(models.Vote, models.Post.id == models.Vote.post_id)
                .where(or_(models.Post.title.ilike(f"%{params.q}%"), 
                       models.Post.content.ilike(f"%{params.q}%"),
                       models.User.email.ilike(f"%{params.q}%")))
                .group_by(models.Post.id, models.User.id)
                .order_by(models.Post.created_at.desc()).offset(params.offset).limit(params.limit))
    posts = db.execute(stmt).mappings().all()
    return posts
    
    