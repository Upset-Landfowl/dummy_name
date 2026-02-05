from app.models import Vote, User, Post
from app.schemas import VoteToggle
from app.utils.jwt import get_current_user
from app.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
    )

@router.post("/", status_code=status.HTTP_200_OK)
def vote(vote: VoteToggle, 
         current_user: User = Depends(get_current_user), 
         db: Session = Depends(get_db)):

    stmt = (select(Vote).where(Vote.user_id == current_user.id,
                               Vote.post_id == vote.post_id))
    is_voted = db.execute(stmt).scalar_one_or_none()

    if not is_voted:
        if not vote.dir:
            stmt = (select(Post).where(Post.id == vote.post_id))
            post_exist = db.execute(stmt).scalar_one_or_none()

            if not post_exist:
                raise HTTPException(detail="Post doesn't exist",
                                    status_code=status.HTTP_400_BAD_REQUEST)
            
            return {"post_id": vote.post_id,
                    "stats": {"isLiked": False}}
        

        try: 
            new_vote = Vote(post_id=vote.post_id,
                            user_id=current_user.id)
            
            db.add(new_vote)
            db.commit()

            return {"post_id": vote.post_id,
                    "stats": {"isLiked": True}}
        
        except IntegrityError as err:
            db.rollback()
            
            if isinstance(err.orig, ForeignKeyViolation): #Checks if the error is cause by a FK const violation
                raise HTTPException(detail="Post doesn't exist",
                                    status_code=status.HTTP_400_BAD_REQUEST)
            raise
            
    
    if vote.dir:
        return {"post_id": vote.post_id,
                "stats": {"isLiked": True}}
    
    db.delete(is_voted)
    db.commit()
    return {"post_id": vote.post_id,
            "stats": {"isLiked": False}}

