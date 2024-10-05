from pydantic import BaseModel, Field

# pylint: disable=missing-class-docstring, too-few-public-methods


class RoomBase(BaseModel):
    name: str = Field(max_length=15)


class RoomCreate(RoomBase):
    user_id: str


class RoomResponse(RoomBase):
    id: str
    created_at: str
    created_by: str


class RoomUserResponse(BaseModel):
    user_id: str
    is_admin: bool
    status: str
    created_at: str
