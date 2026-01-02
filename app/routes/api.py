from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid

from app.database import get_db
from app.models import Project, Scene
from app.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
UPLOADS_PATH = os.getenv("UPLOADS_PATH", "/app/uploads")


@router.post("/projects", response_class=HTMLResponse)
async def create_project(
    request: Request, name: str = Form(...), db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return HTMLResponse('<div class="error">Not authenticated</div>', status_code=401)

    project = Project(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)

    return templates.TemplateResponse(
        "partials/project_card.html", {"request": request, "project": project}
    )


@router.delete("/projects/{project_id}", response_class=HTMLResponse)
async def delete_project(
    request: Request, project_id: int, db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return HTMLResponse("", status_code=401)

    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()

    return HTMLResponse("")


@router.post("/projects/{project_id}/scenes", response_class=HTMLResponse)
async def create_scene(
    request: Request,
    project_id: int,
    prompt: str = Form(...),
    reference_image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return HTMLResponse("", status_code=401)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return HTMLResponse('<div class="error">Project not found</div>', status_code=404)

    # Get next order number
    max_order = (
        db.query(Scene)
        .filter(Scene.project_id == project_id)
        .count()
    )

    scene = Scene(project_id=project_id, prompt=prompt, order=max_order)

    # Save uploaded files
    if reference_image and reference_image.filename:
        ext = os.path.splitext(reference_image.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOADS_PATH, "images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(await reference_image.read())
        scene.reference_image_path = filepath

    if audio and audio.filename:
        ext = os.path.splitext(audio.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOADS_PATH, "audio", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(await audio.read())
        scene.audio_path = filepath

    db.add(scene)
    db.commit()
    db.refresh(scene)

    return templates.TemplateResponse(
        "partials/scene_card.html", {"request": request, "scene": scene}
    )


@router.delete("/scenes/{scene_id}", response_class=HTMLResponse)
async def delete_scene(
    request: Request, scene_id: int, db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return HTMLResponse("", status_code=401)

    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if scene:
        db.delete(scene)
        db.commit()

    return HTMLResponse("")


@router.post("/projects/{project_id}/generate")
async def generate_video(
    request: Request, project_id: int, db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"error": "Project not found"}

    # TODO: Queue video generation task with Celery
    from app.tasks.video import generate_project_video

    task = generate_project_video.delay(project_id)

    project.status = "generating"
    db.commit()

    return {"task_id": task.id, "status": "queued"}


@router.get("/tasks/{task_id}/status")
async def task_status(request: Request, task_id: str):
    user = get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}

    from app.tasks.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
    }
