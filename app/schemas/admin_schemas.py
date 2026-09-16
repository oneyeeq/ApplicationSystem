from pydantic import BaseModel, ConfigDict, Field


class AdminCreate(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    tg_admin_id: int | None = None
    username: str | None = None
   


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_admin_id: int | None
    username: str | None = None
    is_active: bool


class AdminUpdate(BaseModel):
    is_active: bool | None = None

class AdminNotificationResponse(BaseModel):
    tg_admin_id: int | None
    username: str | None = None