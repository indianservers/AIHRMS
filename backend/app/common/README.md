# Backend Common

Shared platform code currently includes:

- `app.core`
- `app.db`
- `app.models.user`
- `app.models.audit`
- `app.models.notification`
- `app.models.platform`
- `app.models.workflow_engine`
- common routers listed in `app.module_registry.COMMON_ROUTER_MODULES`

Keep new cross-app services here only when they have no HRMS, CRM, or Project
Management dependency.

