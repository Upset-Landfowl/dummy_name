
from uuid import uuid4
from app import models, schemas
from app.utils import jwt, utils
from app.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.TokenResponse)
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):

    stmt = (
        select(models.User)
        .where(models.User.email == credentials.email)
    )
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        print("Email not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        
    if not utils.verify_password(credentials.password, row.password):
        print(f"Incorrect password for email: {row.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    token = jwt.create_access_token({"sub": str(row.id)})

    refresh_data = jwt.create_refresh_tokens()
    refresh_token, refresh_token_hash = refresh_data

    tokens_to_db = models.RefreshTokens(
            token_id=uuid4(),
            user_id=row.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7))
    
    db.add(tokens_to_db)
    db.commit()
    db.refresh(tokens_to_db)
    
    return {"access_token": token, "token_type": "bearer",
            "refresh_token_id": tokens_to_db.token_id, "refresh_token": refresh_token}


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=schemas.TokenResponse)
def refresh_access_token(refresh_token: schemas.RefreshTokenIn, db: Session = Depends(get_db)):

    now = datetime.now(timezone.utc)

    with db.begin():
        stmt = (
                select(models.RefreshTokens)
                .where(models.RefreshTokens.token_id == refresh_token.refresh_token_id)
                .with_for_update()
            )
        token_row = db.execute(stmt).scalar_one_or_none()

        if token_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        
        if token_row.expires_at < now or token_row.revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        
        if token_row.used_at is not None:

            # LOGGING LOGIC GOES IN HERE:

            # REVOKE ALL REFRESH TOKEN FOR THE USER
            
            stmt = (
                    update(models.RefreshTokens)
                    .where(models.RefreshTokens.user_id == token_row.user_id)
                    .values(revoked=True)
                    )
            db.execute(stmt)
            db.commit()
            
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
        if not utils.verify_password(refresh_token.refresh_token, token_row.token_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        
        
        token_row.used_at = now

        refresh_data = jwt.create_refresh_tokens()
        refresh_token, refresh_token_hash = refresh_data

        tokens_to_db = models.RefreshTokens(
                token_id=uuid4(),
                user_id=token_row.user_id,
                token_hash=refresh_token_hash,
                expires_at=now + timedelta(days=7))
        
        db.add(tokens_to_db)
        db.flush()
        
    new_token = jwt.create_access_token({"sub": str(token_row.user_id)})
    return {"access_token": new_token, "token_type": "bearer", 
            "refresh_token_id": tokens_to_db.token_id, "refresh_token": refresh_token}
