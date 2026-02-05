
from app import models, schemas
from app.utils import jwt
from app.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session

db = get_db
def tester():
    stmt = (select(models.Post.id, 
                   models.Post.title, 
                   models.Post.content, 
                   models.Post.published,
                   models.Post.rating, 
                   models.Post.created_at,
                   models.User.email.label("created_by")
                   )
            .join(models.User, models.Post.user_id == models.User.id, isouter=True))

    
    posts = db.execute(stmt).mappings().all()
    vote_count = db.execute(select(func.count().label("votes")).where(models.Vote.post_id == posts["id"]))
    return posts