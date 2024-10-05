from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
    UserNotAdminOfRoomError,
    UserNotInARoomError,
    UserNotPending,
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


async def user_not_admin_of_room_handler(
    _: Request, exc: UserNotAdminOfRoomError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.detail})


async def user_not_in_a_room_handler(
    _: Request, exc: UserNotInARoomError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.detail})


async def user_not_pending_handler(_: Request, exc: UserNotPending) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.detail})
