from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.auth import (
    get_current_user,
    AUTH_USERNAME,
    AUTH_PASSWORD,
    create_session,
    logout,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
        token = create_session()
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            max_age=60 * 60 * 24 * 7,  # 1 week
            samesite="lax",
        )
        return response
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@router.get("/logout")
async def logout_route(request: Request):
    token = request.cookies.get("session")
    if token:
        logout(token)
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response


@router.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "projects": projects}
    )


@router.get("/projects/{project_id}")
async def project_detail(
    request: Request, project_id: int, db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "project.html", {"request": request, "project": project}
    )
