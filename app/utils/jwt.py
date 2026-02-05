
from httpx import get
from app.dependencies import get_db
from app.models import User
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
import secrets
from app.utils.utils import hash_password
from app.core.config import get_settings

env = get_settings()


SECRET_KEY = env.secret_key
ALGORITHM = env.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = env.access_token_expire_minutes


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    issued_at = datetime.now(timezone.utc)
    expire = (issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": int(expire.timestamp()), "iat": int(issued_at.timestamp())})
    return jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")

        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        user_id: str = sub
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    stmt = select(User).where(User.id == int(user_id))
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
    

def create_refresh_tokens() -> tuple:
    refresh_token = secrets.token_urlsafe(64)
    refresh_token_hash = hash_password(refresh_token)
    return refresh_token, refresh_token_hash


def decode_jwt(token) -> dict:
    return jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])