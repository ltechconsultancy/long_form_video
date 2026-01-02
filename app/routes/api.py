from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

router = APIRouter()


@router.post("/projects")
async def create_project(name: str = Form(...)):
    # TODO: Create project in database
    return {"id": 1, "name": name}


@router.post("/projects/{project_id}/scenes")
async def create_scene(
    project_id: int,
    prompt: str = Form(...),
    reference_image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    # TODO: Create scene in database, save files
    return {"id": 1, "project_id": project_id, "prompt": prompt}


@router.post("/projects/{project_id}/generate")
async def generate_video(project_id: int):
    # TODO: Queue video generation task
    return {"task_id": "placeholder", "status": "queued"}


@router.get("/tasks/{task_id}/status")
async def task_status(task_id: str):
    # TODO: Get task status from Celery
    return {"task_id": task_id, "status": "pending", "progress": 0}
