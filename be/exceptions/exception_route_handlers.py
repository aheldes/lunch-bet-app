from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
)

# pylint: disable=missing-function-docstring


async def room_name_not_unique_error_handler(
    _: Request, exc: RoomNameNotUniqueError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


async def room_not_found_error_handler(
    _: Request, exc: RoomNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


async def user_already_in_room_error_handler(
    _: Request, exc: UserAlreadyInRoomError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.detail})
