# HRMS Module

HRMS is now registered as a deployable app through `app.module_registry`.

The existing HRMS backend packages still live under `app.api.v1`, `app.models`,
`app.schemas`, and `app.crud` for import compatibility. The registry is the
deployment boundary: HRMS routers and models load only when `INSTALLED_APPS`
contains `hrms`.

Next cleanup step: move each HRMS API/model/schema file into this folder once
the shared identity profile is separated from `Employee`.

