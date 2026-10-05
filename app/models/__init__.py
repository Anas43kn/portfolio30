from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="admin", index=True)


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, default="")


class ImpactMetric(Base):
    __tablename__ = "impact_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(String(80))
    label: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class CaseStudy(Base, TimestampMixin):
    __tablename__ = "case_studies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    subtitle: Mapped[str] = mapped_column(String(255), default="")
    tag: Mapped[str] = mapped_column(String(120), default="")
    short_description: Mapped[str] = mapped_column(Text, default="")
    context: Mapped[str] = mapped_column(Text, default="")
    constraint: Mapped[str] = mapped_column(Text, default="")
    architecture_summary: Mapped[str] = mapped_column(Text, default="")
    outcome_summary: Mapped[str] = mapped_column(Text, default="")
    code_line: Mapped[str] = mapped_column(Text, default="")
    stack: Mapped[str] = mapped_column(String(255), default="")
    impact: Mapped[str] = mapped_column(String(255), default="")
    cover_image: Mapped[str] = mapped_column(String(255), default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    sections: Mapped[list["CaseStudySection"]] = relationship(
        back_populates="case_study",
        cascade="all, delete-orphan",
        order_by="CaseStudySection.display_order",
    )


class CaseStudySection(Base):
    __tablename__ = "case_study_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_study_id: Mapped[int] = mapped_column(ForeignKey("case_studies.id"))
    title: Mapped[str] = mapped_column(String(180))
    content: Mapped[str] = mapped_column(Text, default="")
    section_type: Mapped[str] = mapped_column(String(80), default="text")
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    case_study: Mapped[CaseStudy] = relationship(back_populates="sections")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    stack: Mapped[str] = mapped_column(String(255), default="")
    impact: Mapped[str] = mapped_column(String(255), default="")
    project_type: Mapped[str] = mapped_column(String(120), default="")
    cover_image: Mapped[str] = mapped_column(String(255), default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    icon_label: Mapped[str] = mapped_column(String(120), default="")
    cover_image: Mapped[str] = mapped_column(String(255), default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class BlogPost(Base, TimestampMixin):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    excerpt: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), default="")
    tags: Mapped[str] = mapped_column(String(255), default="")
    cover_image: Mapped[str] = mapped_column(String(255), default="")
    content_format: Mapped[str] = mapped_column(String(40), default="plain")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ExperienceEntry(Base):
    __tablename__ = "experience_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(220))
    meta: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class SystemLayer(Base):
    __tablename__ = "system_layers"

    id: Mapped[int] = mapped_column(primary_key=True)
    layer_key: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    items_json: Mapped[str] = mapped_column(Text, default="[]")
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class ApproachItem(Base):
    __tablename__ = "approach_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(120), default="homepage")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    contact_email: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(80), default="lead")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClientProject(Base, TimestampMixin):
    __tablename__ = "client_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    title: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="planned")
