
from datetime import datetime
from fastapi import Query
from pydantic import BaseModel, ConfigDict, constr, EmailStr, Field
from typing import Annotated
from uuid import UUID

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Annotated[int, Field(ge=1, le=5)] | None = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    created_by: str | None
    votes: int | None

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    rating: Annotated[int, Field(ge=1, le=5)] | None = None


class UserBase(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserCreate(UserBase):
    pass

class UserOut(BaseModel):
    #id: int
    email: str
    #created_at: datetime
    #detail: str

    #model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

"""class UserLoginResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)"""

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str

class TokenResponse(RefreshTokenResponse):
    refresh_token_id: UUID
    refresh_token: str

class RefreshTokenIn(BaseModel):
    refresh_token_id: str
    refresh_token: str

class QueryParams(BaseModel):
    limit: Annotated[int, Query(10, ge=1, le=100)]
    offset: Annotated[int, Query(0)]
    q: Annotated[str | None, Query(default=None)]

class VoteToggle(BaseModel):
    post_id: int
    dir: Annotated[int, Field(ge=0, le=1)]