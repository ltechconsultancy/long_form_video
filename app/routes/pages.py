from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/projects/{project_id}")
async def project_detail(request: Request, project_id: int):
    return templates.TemplateResponse(
        "project.html", {"request": request, "project_id": project_id}
    )
