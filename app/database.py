from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _add_sqlite_columns()


def _add_sqlite_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    columns_by_table = {
        "projects": {
            "cover_image": "VARCHAR(255) DEFAULT ''",
        },
        "services": {
            "cover_image": "VARCHAR(255) DEFAULT ''",
        },
        "blog_posts": {
            "cover_image": "VARCHAR(255) DEFAULT ''",
            "content_format": "VARCHAR(40) DEFAULT 'plain'",
        },
    }

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table, columns in columns_by_table.items():
            if table not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table)}
            for column_name, column_sql in columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_sql}"))
