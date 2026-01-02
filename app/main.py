from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.routes import pages, api
from app.database import engine, Base
from app.models import Project, Scene  # noqa: F401 - needed for Base.metadata


def run_migrations():
    """Add missing columns to existing tables."""
    migrations = [
        # Add new columns to projects table if they don't exist
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='image_model') THEN
                ALTER TABLE projects ADD COLUMN image_model VARCHAR(100) DEFAULT 'fal-ai/flux/schnell';
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='video_model') THEN
                ALTER TABLE projects ADD COLUMN video_model VARCHAR(100) DEFAULT 'fal-ai/ovi/image-to-video';
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='image_size') THEN
                ALTER TABLE projects ADD COLUMN image_size VARCHAR(50) DEFAULT 'landscape_16_9';
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='projects' AND column_name='video_duration') THEN
                ALTER TABLE projects ADD COLUMN video_duration INTEGER DEFAULT 5;
            END IF;
        END $$;
        """,
    ]

    with engine.connect() as conn:
        for migration in migrations:
            try:
                conn.execute(text(migration))
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    Base.metadata.create_all(bind=engine)
    # Run migrations for existing tables
    run_migrations()
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
