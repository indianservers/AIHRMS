"""Project Management schema compatibility helpers."""

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


def _columns(db: Session, table_name: str) -> set[str]:
    try:
        inspector = inspect(db.bind)
        if not inspector.has_table(table_name):
            return set()
        return {column["name"] for column in inspector.get_columns(table_name)}
    except Exception:
        return set()


def ensure_pms_schema(db: Session) -> None:
    """Keep existing dev databases compatible with the PMS models when create_all is used."""
    sprint_columns = _columns(db, "pms_sprints")
    if not sprint_columns:
        return
    additions = {
        "completed_by_user_id": "INTEGER",
        "review_notes": "TEXT",
        "retrospective_notes": "TEXT",
        "what_went_well": "TEXT",
        "what_did_not_go_well": "TEXT",
        "outcome": "TEXT",
    }
    for column_name, column_type in additions.items():
        if column_name not in sprint_columns:
            db.execute(text(f"ALTER TABLE pms_sprints ADD COLUMN {column_name} {column_type}"))
    time_log_columns = _columns(db, "pms_time_logs")
    if time_log_columns and "timesheet_id" not in time_log_columns:
        db.execute(text("ALTER TABLE pms_time_logs ADD COLUMN timesheet_id INTEGER"))
    db.commit()
