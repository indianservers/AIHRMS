"""Create or repair the local AI HRMS database.

This script is intentionally stronger than a bare CREATE DATABASE command:
it creates the configured MySQL database, creates any missing tables, adds
missing ORM columns for drifted local databases, runs Alembic to head, and
seeds the default roles/demo records.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pymysql
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateColumn

from app.core.config import settings


def create_database() -> None:
    connection = pymysql.connect(
        host=settings.MYSQL_SERVER,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        charset="utf8mb4",
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DB}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
        print(f"Database `{settings.MYSQL_DB}` is ready.")
    finally:
        connection.close()


def _column_sql(column, dialect) -> str:
    column_copy = column.copy()
    column_copy.table = None
    return str(CreateColumn(column_copy).compile(dialect=dialect))


def sync_missing_columns() -> None:
    """Add ORM columns missing from an existing local database.

    Alembic remains the source of truth for production migrations. This repair
    pass keeps older developer databases usable when they were created by
    earlier Base.metadata.create_all snapshots.
    """
    import app.db.base  # noqa: F401 - register all SQLAlchemy models
    from app.db.base_class import Base
    from app.db.session import engine

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                ddl = _column_sql(column, engine.dialect)
                connection.execute(text(f"ALTER TABLE `{table.name}` ADD COLUMN {ddl}"))
                print(f"Added missing column {table.name}.{column.name}")


def create_missing_tables() -> None:
    import app.db.base  # noqa: F401 - register all SQLAlchemy models
    from app.db.base_class import Base
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)
    print("Missing tables are ready.")


def run_migrations() -> None:
    root = Path(__file__).resolve().parent
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    config.set_main_option(
        "sqlalchemy.url",
        settings.DATABASE_URL
        or (
            f"mysql+pymysql://{quote_plus(settings.MYSQL_USER)}:"
            f"{quote_plus(settings.MYSQL_PASSWORD)}@{settings.MYSQL_SERVER}:"
            f"{settings.MYSQL_PORT}/{quote_plus(settings.MYSQL_DB)}?charset=utf8mb4"
        ),
    )
    command.upgrade(config, "head")
    print("Alembic migrations are at head.")


def seed_defaults() -> None:
    import app.db.base  # noqa: F401 - register all SQLAlchemy models
    from app.db.init_db import init_db
    from app.db.session import SessionLocal

    for subdir in ["employee_docs", "photos", "resumes", "documents", "certificates", "certificate_imports"]:
        os.makedirs(os.path.join(settings.UPLOAD_DIR, subdir), exist_ok=True)

    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    print("Default roles, permissions, and demo data are seeded.")


def main() -> None:
    create_database()
    create_missing_tables()
    sync_missing_columns()
    run_migrations()
    sync_missing_columns()
    seed_defaults()


if __name__ == "__main__":
    main()
