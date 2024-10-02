from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import disconnect_db, init_db
from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
)
from exceptions.exception_route_handlers import (
    room_name_not_unique_error_handler,
    room_not_found_error_handler,
    user_already_in_room_error_handler,
)
from routes.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Init db on start and disconnects upon shutdown."""
    await init_db()
    yield
    await disconnect_db()


app = FastAPI(lifespan=lifespan)


error_handlers = [
    (RoomNameNotUniqueError, room_name_not_unique_error_handler),
    (RoomNotFoundError, room_not_found_error_handler),
    (UserAlreadyInRoomError, user_already_in_room_error_handler),
]

for handler in error_handlers:
    # Ignore due to bug https://github.com/encode/starlette/pull/2403
    app.add_exception_handler(*handler)  # type: ignore


app.include_router(router)
