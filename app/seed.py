import json
from datetime import datetime

from sqlalchemy import select

from app.auth import hash_password
from app.config import get_settings
from app.database import SessionLocal, init_db
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


def upsert_setting(db, key: str, value: str) -> None:
    setting = db.scalar(select(SiteSetting).where(SiteSetting.key == key))
    if not setting:
        db.add(SiteSetting(key=key, value=value))


def add_if_empty(db, model, rows: list[dict]) -> None:
    if db.scalar(select(model.id).limit(1)):
        return
    for row in rows:
        db.add(model(**row))


def seed_admin(db) -> None:
    settings = get_settings()
    email = settings.admin_email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        db.add(User(email=email, password_hash=hash_password(settings.admin_password), role="admin"))


def seed() -> None:
    init_db()
    with SessionLocal() as db:
        seed_admin(db)
        settings = {
            "name": "YOUR NAME",
            "role": "digital.industrial.systems.architect",
            "hero_title": "I architect scalable production systems across automation and data.",
            "hero_subtitle": "Driving standardization, integration, and production reliability at platform scale.",
            "hero_microline": "// PLC -> Interface -> Data -> Manufacturing",
            "contact_email": "you@example.com",
            "linkedin_url": "/in/yourprofile",
            "location": "Open to high-level automation companies and large manufacturing groups.",
            "cv_url": "",
            "profile_image": "uploads/unnamed.jpg",
            "profile_badges": "Hands-on Architect\nAutomation + Data\nPlatform Scale",
        }
        for key, value in settings.items():
            upsert_setting(db, key, value)

        add_if_empty(
            db,
            ImpactMetric,
            [
                {"value": "40%", "label": "Reduction in machine testing cycle time", "display_order": 1},
                {"value": "EUR 2M", "label": "Industrial machine platforms executed at scale", "display_order": 2},
                {"value": "6 mo", "label": "Industrialization program cycle", "display_order": 3},
                {"value": "Zero", "label": "Tolerance for delivery failure on critical path", "display_order": 4},
            ],
        )

        add_if_empty(
            db,
            Service,
            [
                {
                    "title": "Production Tooling & Internal Applications",
                    "description": "Transform fragile Excel/VBA workflows into structured tools using SQL-backed logic, JavaScript interfaces, and maintainable data models.",
                    "icon_label": "production.tooling",
                    "display_order": 1,
                },
                {
                    "title": "PLC/Web Interface Modernization",
                    "description": "Design and improve production interfaces that connect automation layers with operators, test workflows, and structured data.",
                    "icon_label": "automation.integration",
                    "display_order": 2,
                },
                {
                    "title": "Industrialization Support",
                    "description": "Lock repeatable assembly, electrical integration, testing, and validation workflows so production teams do not restart from zero.",
                    "icon_label": "industrialization",
                    "display_order": 3,
                },
                {
                    "title": "SQL/Data Structuring for Manufacturing",
                    "description": "Move rules, configurations, and traceability workflows into structured data models that production teams can trust.",
                    "icon_label": "data.layer",
                    "display_order": 4,
                },
            ],
        )

        add_if_empty(
            db,
            CaseStudy,
            [
                {
                    "title": "Web-Based PLC Testing Architecture",
                    "slug": "web-based-plc-testing-architecture",
                    "subtitle": "Commissioning system improvement on the critical path.",
                    "tag": "commissioning.system",
                    "short_description": "Replaced legacy HMI workflow and manual PLC data handling with an integrated web interface directly connected to PLC systems.",
                    "context": "Machine testing process for large automated systems in delivery-critical environments.",
                    "constraint": "Legacy workflow relied on USB exports and laptop back-and-forth with PLC data, adding unnecessary steps.",
                    "architecture_summary": "Direct PLC communication from a web interface\nCentralized UI for test execution and validation\nStructured data availability by design, without manual transfers",
                    "outcome_summary": "~40% reduction in testing cycle time\nRemoved manual bottlenecks and fragile handling\nImproved repeatability and operational clarity",
                    "code_line": "// workflow: legacy.usb.loop -> integrated.web.plc.interface\nPLC <-> Web Interface <-> Structured Data -> Test Validation",
                    "stack": "stack: PLC / web / structured data",
                    "impact": "impact: ~40% cycle-time reduction",
                    "display_order": 1,
                    "is_featured": True,
                    "is_published": True,
                },
                {
                    "title": "Excel Chaos -> SQL Rule Engine",
                    "slug": "excel-chaos-sql-rule-engine",
                    "subtitle": "Rules engine standardization at scale.",
                    "tag": "rules.engine",
                    "short_description": "Structured complex configuration logic into a database-backed rule system with a JavaScript execution layer.",
                    "context": "Production tooling built on complex Excel logic and nested rule structures across machine variants.",
                    "constraint": "Spreadsheet logic becomes fragile, hard to maintain, and difficult to scale across platforms.",
                    "architecture_summary": "Rule logic structured into a SQL database\nJavaScript execution layer to apply rules consistently\nClear separation: data model <-> logic <-> interface",
                    "outcome_summary": "Stabilized rule execution and maintainability\nImproved scalability across configurations\nReduced long-term operational fragility",
                    "code_line": "// principle: separate.logic.from.interface\nSQL(rule.model) -> JS(engine) -> outputs(production.artifacts)",
                    "stack": "stack: SQL / JS / Excel migration",
                    "impact": "impact: logic stabilized",
                    "display_order": 2,
                    "is_featured": True,
                    "is_published": True,
                },
                {
                    "title": "Machine Platform Industrialization",
                    "slug": "machine-platform-industrialization",
                    "subtitle": "Prototype-to-production risk containment.",
                    "tag": "platform.scale",
                    "short_description": "Industrialized large automated packaging systems from engineering builds to repeatable production processes.",
                    "context": "Industrialization of large packaging and production-line machinery for final clients, with machines around the EUR 2M scale.",
                    "constraint": "No room for failure: slips affect delivery date, lead time, and project margin.",
                    "architecture_summary": "Locked repeatable assembly and integration processes\nCoordinated electrical integration and safety debugging\nValidated procedures so production does not rebuild from scratch",
                    "outcome_summary": "Reduced rework risk across future builds\nImproved production readiness and repeatability\nProtected delivery timelines under high constraints",
                    "code_line": "// industrialization: prototype -> repeatable.production\nprocess.lock-in -> integration.standardization -> delivery.protection",
                    "stack": "scope: EUR 2M platforms / 6-month cycles",
                    "impact": "impact: risk contained",
                    "display_order": 3,
                    "is_featured": True,
                    "is_published": True,
                },
            ],
        )

        add_if_empty(
            db,
            Project,
            [
                {
                    "title": "PLC Test Interface Prototype",
                    "slug": "plc-test-interface-prototype",
                    "description": "A focused prototype for moving machine test execution into a browser-based operator interface.",
                    "stack": "FastAPI / JS / PLC data model",
                    "impact": "reduced manual test loops",
                    "project_type": "internal.tool",
                    "display_order": 1,
                    "is_published": True,
                },
                {
                    "title": "Manufacturing Rule Viewer",
                    "slug": "manufacturing-rule-viewer",
                    "description": "A lightweight interface for inspecting SQL-backed production configuration rules without opening fragile spreadsheets.",
                    "stack": "SQL / server-rendered UI",
                    "impact": "clearer rule ownership",
                    "project_type": "data.tool",
                    "display_order": 2,
                    "is_published": True,
                },
            ],
        )

        add_if_empty(
            db,
            ExperienceEntry,
            [
                {
                    "period": "202X -> Present",
                    "title": "Industrial Systems Architect / Automation Engineer",
                    "meta": "manufacturing / automation / production integration",
                    "description": "Drove standardization and integration across PLC, interface, and data layers. Modernized commissioning workflows and stabilized production processes under delivery-critical constraints.",
                    "display_order": 1,
                },
                {
                    "period": "Key Missions",
                    "title": "Industrialization & Platform Transition",
                    "meta": "6 months / EUR 2M machinery / cross-disciplinary integration",
                    "description": "Structured prototype-to-production workflows to prevent reset-to-zero rebuilds. Coordinated electrical integration and safety debugging alongside production teams.",
                    "display_order": 2,
                },
                {
                    "period": "Operations",
                    "title": "Production IT Tooling Governance",
                    "meta": "maintenance -> stabilization -> improvement",
                    "description": "Managed and maintained production-facing tools for service and manufacturing needs, reducing operational friction and increasing reliability in day-to-day industrial workflows.",
                    "display_order": 3,
                },
            ],
        )

        add_if_empty(
            db,
            SystemLayer,
            [
                {
                    "layer_key": "automation.layer",
                    "title": "Automation Layer",
                    "description": "PLC and industrial integration constraints.",
                    "items_json": json.dumps(["PLC logic, commissioning, validation", "Industrial networking & connectivity", "Safety debugging and integration constraints"]),
                    "display_order": 1,
                },
                {
                    "layer_key": "application.layer",
                    "title": "Application Layer",
                    "description": "Interfaces that remove manual loops.",
                    "items_json": json.dumps(["Web interfaces for production workflows", "JavaScript integration and UI logic", "Human-proofing: reducing manual steps"]),
                    "display_order": 2,
                },
                {
                    "layer_key": "data.layer",
                    "title": "Data Layer",
                    "description": "Structured rules, traceability, and configuration.",
                    "items_json": json.dumps(["SQL-backed configuration and rules", "Structured data flows and traceability", "Excel-to-database migration strategy"]),
                    "display_order": 3,
                },
            ],
        )

        add_if_empty(
            db,
            ApproachItem,
            [
                {"text": "Reduce fragility in production workflows by removing manual bottlenecks.", "display_order": 1},
                {"text": "Separate logic from interface layers to enable maintainability and scale.", "display_order": 2},
                {"text": "Standardize repeatable integration processes across machine variants.", "display_order": 3},
                {"text": "Design systems for traceability, validation, and delivery reliability.", "display_order": 4},
                {"text": "Prioritize critical-path improvements with measurable time ROI.", "display_order": 5},
            ],
        )

        add_if_empty(
            db,
            BlogPost,
            [
                {
                    "title": "Why Production Tools Fail Quietly",
                    "slug": "why-production-tools-fail-quietly",
                    "excerpt": "A short note on fragile internal tooling, hidden manual loops, and why structured data matters.",
                    "content": "Production tooling usually fails before anyone calls it a failure. The first symptoms are manual corrections, side spreadsheets, and tribal knowledge. The fix starts by separating rules, interface behavior, and data ownership.",
                    "category": "engineering.note",
                    "tags": "production tooling, sql, reliability",
                    "is_published": True,
                    "published_at": datetime.utcnow(),
                }
            ],
        )

        db.commit()


if __name__ == "__main__":
    seed()
