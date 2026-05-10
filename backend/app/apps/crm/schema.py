from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


AUDIT_TABLES = [
    "crm_companies",
    "crm_contacts",
    "crm_leads",
    "crm_pipelines",
    "crm_pipeline_stages",
    "crm_deals",
    "crm_products",
    "crm_quotations",
    "crm_activities",
    "crm_tasks",
    "crm_notes",
    "crm_email_logs",
    "crm_call_logs",
    "crm_meetings",
    "crm_tickets",
    "crm_campaigns",
    "crm_file_assets",
    "crm_custom_field_values",
]


def ensure_crm_schema(db: Session) -> None:
    """Keep dev databases compatible with CRM models when create_all is used."""
    inspector = inspect(db.bind)
    tables = set(inspector.get_table_names())
    for table_name in AUDIT_TABLES:
        if table_name not in tables:
            continue
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "created_by_user_id" not in columns:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN created_by_user_id INTEGER"))
        if "updated_by_user_id" not in columns:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN updated_by_user_id INTEGER"))
        if "deleted_at" not in columns and table_name not in {"crm_deal_products", "crm_quotation_items", "crm_campaign_leads", "crm_tags"}:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN deleted_at DATETIME"))
        if table_name in {"crm_email_logs", "crm_call_logs", "crm_meetings"} and "owner_user_id" not in columns:
            db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN owner_user_id INTEGER"))
        if table_name == "crm_pipeline_stages" and "organization_id" not in columns:
            db.execute(text("ALTER TABLE crm_pipeline_stages ADD COLUMN organization_id INTEGER"))
            columns.add("organization_id")
        if "organization_id" in columns:
            db.execute(text(f"UPDATE {table_name} SET organization_id = 1 WHERE organization_id IS NULL"))
    db.commit()
