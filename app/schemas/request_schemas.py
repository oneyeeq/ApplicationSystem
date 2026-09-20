from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.request_model import StatusEnum


class RequestCreate(BaseModel):
    service_name: str = Field(min_length=1, max_length=255)
    phone_number: str = Field(min_length=1, max_length=32)


class RequestUpdate(BaseModel):
    status: StatusEnum


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_name: str
    phone_number: str
    user_id: int
    status: StatusEnum
    created_at: datetime
    updated_at: datetime


class PaginatedRequestsResponse(BaseModel):
    items: list[RequestResponse]
    total: int
    page: int
    page_size: int
