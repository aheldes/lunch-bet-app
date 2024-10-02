from contextlib import asynccontextmanager

from database.engine import disconnect_db, get_session, init_db
from database.models import Room
from fastapi import Depends, FastAPI, HTTPException
from schemas import RoomCreate, RoomResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Init db on start and disconnects upon shutdown."""
    await init_db()
    yield
    await disconnect_db()


app = FastAPI(lifespan=lifespan)


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
