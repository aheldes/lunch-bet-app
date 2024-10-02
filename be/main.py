from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import disconnect_db, get_session, init_db, Room, RoomUser
from dependencies import join_room_dependency
from dependencies.errors import RoomNotFoundError, UserAlreadyInRoomError
from schemas import RoomCreate, RoomResponse, RoomJoinRequest


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Init db on start and disconnects upon shutdown."""
    await init_db()
    yield
    await disconnect_db()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RoomNotFoundError)
async def room_not_found_error_handler(_, exc: RoomNotFoundError) -> JSONResponse:
    """Error handler for RoomNotFoundError"""
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(UserAlreadyInRoomError)
async def user_already_in_room_error_handler(
    _, exc: UserAlreadyInRoomError
) -> JSONResponse:
    """Error handler for UserAlreadyInRoomError"""
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.post("/rooms/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new room with the provided name and user ID."""
    new_room = Room(name=room_data.name, created_by=room_data.user_id)
    try:
        session.add(new_room)
        await session.commit()
        await session.refresh(new_room)
        return new_room
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=400, detail="Room name must be unique."
        ) from exc


@app.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,  # pylint: disable=unused-argument
    join_request: RoomJoinRequest,  # pylint: disable=unused-argument
    _: RoomUser = Depends(join_room_dependency),
):
    """Request to join a room."""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)
