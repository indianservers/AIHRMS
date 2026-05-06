# Multi-App Architecture

The suite now supports deployable product modules through environment-driven
registries.

Umbrella product name: **Business Suite**.

Apps:

- HRMS
- KaryaFlow: Project Management
- VyaparaCRM: CRM

## Backend

Use `INSTALLED_APPS` to select backend routers, models, and seed behavior.

Examples:

```env
INSTALLED_APPS=hrms
```

```env
INSTALLED_APPS=crm,project_management
```

Current modules:

- `hrms`
- `crm`
- `project_management`

Common platform code is loaded for every deployment: auth, users, audit, base
database setup, security, logs, and workflow engine.

## Table Naming

Use lowercase prefixes so table names stay portable across MySQL, PostgreSQL,
Windows, and Linux deployments.

- Common/shared tables: `common_<name>`
- HRMS tables: `hrms_<name>`
- Project Management/KaryaFlow tables: `pms_<name>`
- CRM/VyaparaCRM tables: `crm_<name>`

Existing HRMS tables still use their original names. New app tables should use
the prefix rule immediately. Renaming current HRMS/common tables should be done
later with explicit Alembic migrations, not by casual model edits.

Examples:

```txt
common_users
common_organizations
common_files
hrms_employees
hrms_payroll_runs
pms_projects
pms_tasks
crm_leads
crm_deals
```

## Frontend

Use `VITE_INSTALLED_APPS` to select visible routes and navigation.

Examples:

```env
VITE_INSTALLED_APPS=hrms
```

```env
VITE_INSTALLED_APPS=crm,project_management
```

HRMS pages now live under `frontend/src/apps/hrms/pages`. Login remains shared
under `frontend/src/pages/auth`.

## Next Refactor

`User` and `Employee` are partially decoupled, but HRMS still owns the employee
profile. Before CRM-only or Project-only production rollout, add a common
`profiles` or `people` table so common services never need HRMS employee data.
