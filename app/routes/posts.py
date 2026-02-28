
from app import models, schemas
from app.utils import jwt
from app.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound



router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)



@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.PostResponse])
def get_posts(params: schemas.QueryParams = Depends(), current_user: models.User = Depends(jwt.get_current_user),
    db: Session = Depends(get_db)):
    
    stmt = (select(models.Post.id, 
                   models.Post.title, 
                   models.Post.content, 
                   models.Post.published,
                   models.Post.rating, 
                   models.Post.created_at,
                   models.User.email.label("created_by"),
                   func.count(models.Vote.post_id).label("votes")
                   )
            .join(models.User, models.Post.user_id == models.User.id, isouter=True)
            .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
            .group_by(models.Post.id, models.User.id)
            .order_by(models.Post.created_at.desc())
            .offset(params.offset)
            .limit(params.limit))
    
    posts = db.execute(stmt).mappings().all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, current_user: models.User = Depends(jwt.get_current_user), db: Session = Depends(get_db)):

    new_post_data = post.model_dump()
    new_post_data.update({"user_id": current_user.id})
    new_post = models.Post(**new_post_data)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    stmt = (
    select(
        models.Post.id, 
        models.Post.title, 
        models.Post.content, 
        models.Post.published,
        models.Post.rating, 
        models.Post.created_at,
        models.User.email.label("created_by"),
        func.count(models.Vote.post_id).label("votes")
    )
    .join(models.User, models.Post.user_id == models.User.id)      
    .outerjoin(models.Vote, models.Post.id == models.Vote.post_id) 
    .where(models.Post.id == new_post.id)
    .group_by(models.Post.id, models.User.id)
)

    postt = db.execute(stmt).mappings().one()
    return postt

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def get_post(id: int, current_user: models.User = Depends(jwt.get_current_user), db: Session = Depends(get_db)):

    stmt = (
            select(models.Post.id, 
                   models.Post.title, 
                   models.Post.content, 
                   models.Post.published,
                   models.Post.rating, 
                   models.Post.created_at,
                   models.User.email.label("created_by"),
                   func.count(models.Vote.post_id).label("votes"))
            .join(models.User, models.Post.user_id == models.User.id)
            .join(models.Vote, models.Post.id == models.Vote.post_id)
            .where(models.Post.id == id)
            .group_by(models.Post.id, models.User.id)
    )
    
    try:
        post = db.execute(stmt).mappings().one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def put_update(id: int, post: schemas.PostCreate, current_user: models.User = Depends(jwt.get_current_user), 
               db: Session = Depends(get_db)):

    stmt = (
        update(models.Post)
        .where(models.Post.id == id)
        .values(**post.model_dump())
        .returning(models.Post) 
    )
    result = db.execute(stmt)
    updated_post = result.scalar_one_or_none()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db.commit()
    return updated_post

@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def patch_update(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):

    stmt = (
        update(models.Post)
        .where(models.Post.id == id)
        .values(**post.model_dump(exclude_unset=True))
        .returning(models.Post)
    )

    result = db.execute(stmt)
    updated_post = result.scalar_one_or_none()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.") 
    db.commit()
    return updated_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    result = db.execute(delete(models.Post).where(models.Post.id == id))
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db.commit()
    return
