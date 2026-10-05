import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ApproachItem,
    BlogPost,
    CaseStudy,
    ExperienceEntry,
    ImpactMetric,
    NewsletterSubscriber,
    Project,
    Service,
    SiteSetting,
    SystemLayer,
)


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ordered(model, active_field: str | None = None):
    statement = select(model).order_by(model.display_order.asc(), model.id.asc())
    if active_field:
        statement = statement.where(getattr(model, active_field).is_(True))
    return statement


def settings_map(db: Session) -> dict[str, str]:
    rows = db.scalars(select(SiteSetting)).all()
    return {row.key: row.value for row in rows}


def public_context(request: Request, db: Session, **extra):
    context = {"request": request, "settings": settings_map(db)}
    context.update(extra)
    return context


def split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    layers = db.scalars(ordered(SystemLayer, "is_active")).all()
    layer_view = [
        {
            "layer": layer,
            "layer_items": json.loads(layer.items_json or "[]"),
        }
        for layer in layers
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": settings_map(db),
            "impact_metrics": db.scalars(ordered(ImpactMetric, "is_active")).all(),
            "case_studies": db.scalars(
                select(CaseStudy)
                .where(CaseStudy.is_featured.is_(True), CaseStudy.is_published.is_(True))
                .order_by(CaseStudy.display_order.asc(), CaseStudy.id.asc())
            ).all(),
            "services": db.scalars(ordered(Service, "is_active")).all(),
            "projects": db.scalars(
                select(Project)
                .where(Project.is_published.is_(True))
                .order_by(Project.display_order.asc(), Project.id.asc())
                .limit(6)
            ).all(),
            "experience_entries": db.scalars(ordered(ExperienceEntry, "is_active")).all(),
            "system_layers": layer_view,
            "approach_items": db.scalars(ordered(ApproachItem, "is_active")).all(),
            "blog_posts": db.scalars(
                select(BlogPost)
                .where(BlogPost.is_published.is_(True))
                .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc())
                .limit(3)
            ).all(),
            "signup_status": request.query_params.get("signup"),
        },
    )


@router.get("/case-studies")
def case_studies(request: Request, db: Session = Depends(get_db)):
    items = db.scalars(
        select(CaseStudy)
        .where(CaseStudy.is_published.is_(True))
        .order_by(CaseStudy.display_order.asc(), CaseStudy.id.asc())
    ).all()
    return templates.TemplateResponse("case_studies.html", public_context(request, db, case_studies=items))


@router.get("/case-studies/{slug}")
def case_study_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    item = db.scalar(select(CaseStudy).where(CaseStudy.slug == slug, CaseStudy.is_published.is_(True)))
    if not item:
        return templates.TemplateResponse("404.html", public_context(request, db), status_code=404)
    return templates.TemplateResponse("case_study_detail.html", public_context(request, db, case_study=item, split_lines=split_lines))


@router.get("/projects")
def projects_index(request: Request, db: Session = Depends(get_db)):
    projects = db.scalars(
        select(Project)
        .where(Project.is_published.is_(True))
        .order_by(Project.display_order.asc(), Project.id.asc())
    ).all()
    return templates.TemplateResponse("projects.html", public_context(request, db, projects=projects))


@router.get("/projects/{slug}")
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    project = db.scalar(select(Project).where(Project.slug == slug, Project.is_published.is_(True)))
    if not project:
        return templates.TemplateResponse("404.html", public_context(request, db), status_code=404)
    return templates.TemplateResponse("project_detail.html", public_context(request, db, project=project))


@router.get("/blog")
def blog_index(request: Request, db: Session = Depends(get_db)):
    posts = db.scalars(
        select(BlogPost)
        .where(BlogPost.is_published.is_(True))
        .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc())
    ).all()
    return templates.TemplateResponse("blog.html", public_context(request, db, blog_posts=posts))


@router.get("/blog/{slug}")
def blog_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.scalar(select(BlogPost).where(BlogPost.slug == slug, BlogPost.is_published.is_(True)))
    if not post:
        return templates.TemplateResponse("404.html", public_context(request, db), status_code=404)
    return templates.TemplateResponse("blog_detail.html", public_context(request, db, post=post))


@router.post("/newsletter")
def newsletter_signup(email: str = Form(...), db: Session = Depends(get_db)):
    clean_email = email.lower().strip()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_email):
        return RedirectResponse("/?signup=invalid#contact", status_code=303)
    existing = db.scalar(select(NewsletterSubscriber).where(NewsletterSubscriber.email == clean_email))
    if not existing:
        db.add(NewsletterSubscriber(email=clean_email, source="homepage", created_at=datetime.utcnow()))
        db.commit()
    return RedirectResponse("/?signup=ok#contact", status_code=303)


@router.get("/client")
def client_reserved(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("client_reserved.html", public_context(request, db))
