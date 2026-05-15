from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class NoteUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    access: str


class ShareRequest(BaseModel):
    username: str


class MessageResponse(BaseModel):
    message: str
