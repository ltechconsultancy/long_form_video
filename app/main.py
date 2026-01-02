from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.routes import pages, api
from app.database import engine, Base
from app.models import Project, Scene  # noqa: F401 - needed for Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown


app = FastAPI(title="Long Form Video Generator", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount uploads folder for serving generated videos
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# Include routers
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")
