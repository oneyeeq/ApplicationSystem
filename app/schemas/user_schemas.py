from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    tg_user_id: int
    username: str | None = Field(default=None, max_length=255)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_user_id: int
    username: str | None
    is_active: bool
    active_requests: int


class UserUpdate(BaseModel):
    is_active: bool | None = None
