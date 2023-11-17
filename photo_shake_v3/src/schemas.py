from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.database.models import UserRoleEnum


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=30)
    avatar: Optional[str]


class UserUpdateModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    
    
class UserResponseModel(BaseModel):
    id: int
    username: str
    email: str
    is_active: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True
    
class UserProfileModel(BaseModel):
    username: str 
    email: EmailStr
    avatar: Optional[str]
    foto_count: Optional[int]
    comment_count: Optional[int]
    rates_count: Optional[int]
    is_active: Optional[bool]
    created_at: datetime
    
    
class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str]
    role: UserRoleEnum
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"
    
    
class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TagBase(BaseModel):
    title: str = Field(max_length=50)


class TagModel(TagBase):
    pass

    class Config:
        from_attributes = True


class TagResponse(TagBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    text: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    created_at: datetime
    # updated_at: Optional[datetime] # було
    user_id: int
    foto_id: int
    update_status: bool = False

    class Config:
        from_attributes = True


class CommentUpdate(CommentModel):
    update_status: bool = True
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RatingBase(BaseModel):
    rate: int


class RatingModel(RatingBase):
    id: int
    created_at: datetime
    foto_id: int
    user_id: int

    class Config:
        from_attributes = True


class FotoBase(BaseModel):
    id: int
    image_url: str = Field(max_length=300, default=None)
    transform_url: str = Field(max_length=450, default=None)
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    tags: List[str] = []

    @validator("tags")
    def validate_tags(cls, v):
        if len(v or []) > 5:
            raise ValueError("Too many tags. Maximum 5 tags allowed.")
        return v


class FotoModel(FotoBase):
    pass


class FotoUpdate(BaseModel):
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    tags: List[str]
    

class FotoResponse(FotoBase):
    tags: List[TagModel]
    avg_rating: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RequestEmail(BaseModel):
    email: EmailStr


class RequestRole(BaseModel):
    email: EmailStr
    role: UserRoleEnum
