from fastapi import APIRouter

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.get("/module-info")
def module_info():
    return {
        "key": "crm",
        "name": "VyaparaCRM",
        "status": "installed",
        "modules": [
            "leads",
            "contacts",
            "companies",
            "pipelines",
            "pipeline-stages",
            "deals",
            "products",
            "quotations",
            "activities",
            "tasks",
            "notes",
            "email-logs",
            "call-logs",
            "meetings",
            "tickets",
            "campaigns",
            "files",
            "tags",
        ],
    }
