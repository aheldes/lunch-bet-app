from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import disconnect_db, init_db
from exceptions.exception_route_handlers import error_handlers
from routes.routes import router
from routes.ws_routes import router as ws_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Init db on start and disconnects upon shutdown."""
    await init_db()
    yield
    await disconnect_db()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for handler in error_handlers:
    # Ignore due to bug https://github.com/encode/starlette/pull/2403
    app.add_exception_handler(*handler)  # type: ignore


app.include_router(router)
app.include_router(ws_router)
