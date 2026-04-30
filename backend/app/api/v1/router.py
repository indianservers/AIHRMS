from fastapi import APIRouter
from app.api.v1 import (
    ai,
    assets,
    attendance,
    auth,
    company,
    documents,
    employees,
    exit,
    helpdesk,
    leave,
    onboarding,
    payroll,
    performance,
    recruitment,
    reports,
    targets,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(company.router)
api_router.include_router(employees.router)
api_router.include_router(attendance.router)
api_router.include_router(leave.router)
api_router.include_router(payroll.router)
api_router.include_router(recruitment.router)
api_router.include_router(performance.router)
api_router.include_router(helpdesk.router)
api_router.include_router(reports.router)
api_router.include_router(targets.router)
api_router.include_router(ai.router)
api_router.include_router(assets.router)
api_router.include_router(documents.router)
api_router.include_router(onboarding.router)
api_router.include_router(exit.router)
