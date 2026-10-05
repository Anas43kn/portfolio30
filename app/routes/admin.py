import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models import (
    ApproachItem,
    BlogPost,
    CaseStudy,
    ExperienceEntry,
    ImpactMetric,
    Project,
    Service,
    SiteSetting,
    SystemLayer,
    User,
)


router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = Path("app/static/uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


ENTITY_CONFIG: dict[str, dict[str, Any]] = {
    "case-studies": {
        "model": CaseStudy,
        "title": "Case Studies",
        "fields": [
            "title",
            "slug",
            "subtitle",
            "tag",
            "short_description",
            "context",
            "constraint",
            "architecture_summary",
            "outcome_summary",
            "code_line",
            "stack",
            "impact",
            "cover_image",
            "display_order",
            "is_featured",
            "is_published",
        ],
        "long": {"short_description", "context", "constraint", "architecture_summary", "outcome_summary", "code_line"},
        "images": {"cover_image"},
        "bools": {"is_featured", "is_published"},
        "status": "is_published",
        "public_prefix": "/case-studies",
    },
    "projects": {
        "model": Project,
        "title": "Projects",
        "fields": ["title", "slug", "description", "stack", "impact", "project_type", "cover_image", "display_order", "is_published"],
        "long": {"description"},
        "images": {"cover_image"},
        "bools": {"is_published"},
        "status": "is_published",
    },
    "blogs": {
        "model": BlogPost,
        "title": "Blog Posts",
        "fields": ["title", "slug", "excerpt", "content", "category", "tags", "cover_image", "content_format", "is_published"],
        "long": {"excerpt", "content"},
        "images": {"cover_image"},
        "bools": {"is_published"},
        "status": "is_published",
        "public_prefix": "/blog",
    },
    "services": {
        "model": Service,
        "title": "Services",
        "fields": ["title", "description", "icon_label", "cover_image", "display_order", "is_active"],
        "long": {"description"},
        "images": {"cover_image"},
        "bools": {"is_active"},
        "status": "is_active",
    },
    "impact": {
        "model": ImpactMetric,
        "title": "Impact Metrics",
        "fields": ["value", "label", "description", "display_order", "is_active"],
        "long": {"description"},
        "bools": {"is_active"},
        "status": "is_active",
    },
    "experience": {
        "model": ExperienceEntry,
        "title": "Experience",
        "fields": ["period", "title", "meta", "description", "display_order", "is_active"],
        "long": {"description"},
        "bools": {"is_active"},
        "status": "is_active",
    },
    "system-layers": {
        "model": SystemLayer,
        "title": "System Layers",
        "fields": ["layer_key", "title", "description", "items_json", "display_order", "is_active"],
        "long": {"description", "items_json"},
        "bools": {"is_active"},
        "status": "is_active",
    },
    "approach": {
        "model": ApproachItem,
        "title": "Approach",
        "fields": ["text", "display_order", "is_active"],
        "long": {"text"},
        "bools": {"is_active"},
        "status": "is_active",
    },
}


SETTING_KEYS = [
    "name",
    "role",
    "hero_title",
    "hero_subtitle",
    "hero_microline",
    "contact_email",
    "linkedin_url",
    "location",
    "cv_url",
    "profile_image",
    "profile_badges",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def admin_context(request: Request, current_user: User, **extra):
    context = {"request": request, "current_user": current_user, "entities": ENTITY_CONFIG}
    context.update(extra)
    return context


def coerce_value(field: str, value: str):
    if field == "display_order":
        return int(value or 0)
    if field == "items_json":
        try:
            parsed = json.loads(value or "[]")
            return json.dumps(parsed)
        except json.JSONDecodeError:
            lines = [line.strip("- ").strip() for line in value.splitlines() if line.strip()]
            return json.dumps(lines)
    return value.strip()


async def save_image_upload(upload) -> str:
    if not upload or not getattr(upload, "filename", ""):
        return ""

    extension = Path(upload.filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg, png, webp, and gif images are allowed.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / filename
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    total = 0
    with destination.open("wb") as output:
        while chunk := await upload.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                output.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Image uploads are limited to {get_settings().max_upload_mb} MB.",
                )
            output.write(chunk)
    return f"uploads/{filename}"


def populate_item(item, form, config):
    bools = config.get("bools", set())
    for field in config["fields"]:
        if field in bools:
            setattr(item, field, form.get(field) == "on")
        else:
            setattr(item, field, coerce_value(field, form.get(field, "")))
    if hasattr(item, "slug") and not getattr(item, "slug", ""):
        item.slug = slugify(getattr(item, "title", "untitled"))
    if isinstance(item, BlogPost) and item.is_published and not item.published_at:
        item.published_at = datetime.utcnow()


async def apply_image_uploads(item, form, config):
    for field in config.get("images", set()):
        uploaded_path = await save_image_upload(form.get(f"{field}_file"))
        if uploaded_path:
            setattr(item, field, uploaded_path)


def item_label(item) -> str:
    return getattr(item, "title", None) or getattr(item, "label", None) or getattr(item, "text", "")[:80]


@router.get("")
def dashboard(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    counts = {
        key: db.scalar(select(config["model"]).count()) if False else len(db.scalars(select(config["model"])).all())
        for key, config in ENTITY_CONFIG.items()
    }
    return templates.TemplateResponse("admin/dashboard.html", admin_context(request, current_user, counts=counts))


@router.get("/settings")
def settings_page(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = {row.key: row.value for row in db.scalars(select(SiteSetting)).all()}
    return templates.TemplateResponse("admin/settings.html", admin_context(request, current_user, settings=rows, keys=SETTING_KEYS))


@router.post("/settings")
async def save_settings(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    form = await request.form()
    for key in SETTING_KEYS:
        setting = db.scalar(select(SiteSetting).where(SiteSetting.key == key))
        if not setting:
            setting = SiteSetting(key=key)
            db.add(setting)
        setting.value = str(form.get(key, "")).strip()
    profile_upload = await save_image_upload(form.get("profile_image_file"))
    if profile_upload:
        setting = db.scalar(select(SiteSetting).where(SiteSetting.key == "profile_image"))
        if not setting:
            setting = SiteSetting(key="profile_image")
            db.add(setting)
        setting.value = profile_upload
    db.commit()
    return RedirectResponse("/admin/settings", status_code=303)


@router.get("/{entity}")
def list_items(entity: str, request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    config = ENTITY_CONFIG[entity]
    model = config["model"]
    order_field = getattr(model, "display_order", None)
    statement = select(model).order_by(order_field.asc(), model.id.asc()) if order_field is not None else select(model).order_by(model.id.desc())
    items = db.scalars(statement).all()
    return templates.TemplateResponse(
        "admin/list.html",
        admin_context(request, current_user, entity=entity, config=config, items=items, item_label=item_label),
    )


@router.get("/{entity}/new")
def new_item(entity: str, request: Request, current_user: User = Depends(require_admin)):
    config = ENTITY_CONFIG[entity]
    return templates.TemplateResponse(
        "admin/form.html",
        admin_context(request, current_user, entity=entity, config=config, item=None),
    )


@router.post("/{entity}/new")
async def create_item(entity: str, request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    config = ENTITY_CONFIG[entity]
    item = config["model"]()
    form = await request.form()
    populate_item(item, form, config)
    await apply_image_uploads(item, form, config)
    db.add(item)
    db.commit()
    return RedirectResponse(f"/admin/{entity}", status_code=303)


@router.get("/{entity}/{item_id}/edit")
def edit_item(entity: str, item_id: int, request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    config = ENTITY_CONFIG[entity]
    item = db.get(config["model"], item_id)
    return templates.TemplateResponse(
        "admin/form.html",
        admin_context(request, current_user, entity=entity, config=config, item=item),
    )


@router.post("/{entity}/{item_id}/edit")
async def update_item(
    entity: str,
    item_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    config = ENTITY_CONFIG[entity]
    item = db.get(config["model"], item_id)
    form = await request.form()
    populate_item(item, form, config)
    await apply_image_uploads(item, form, config)
    db.commit()
    return RedirectResponse(f"/admin/{entity}", status_code=303)


@router.post("/{entity}/{item_id}/toggle")
def toggle_item(entity: str, item_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    config = ENTITY_CONFIG[entity]
    item = db.get(config["model"], item_id)
    status_field = config["status"]
    setattr(item, status_field, not getattr(item, status_field))
    db.commit()
    return RedirectResponse(f"/admin/{entity}", status_code=303)
