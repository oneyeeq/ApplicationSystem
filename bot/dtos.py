from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RequestData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    service_name: str
    phone_number: str
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class RequestCreateData(BaseModel):
    service_name: str
    phone_number: str


class UserData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    tg_user_id: int
    username: str | None
    is_active: bool
    active_requests: int


class AdminData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    tg_admin_id: int
    username: str | None
    is_active: bool


class CanCreateRequestData(BaseModel):
    allowed: bool
    error: str | None = None
