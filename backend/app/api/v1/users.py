from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.employee import Employee
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


def _user_company_id(user: User) -> int:
    employee = getattr(user, "employee", None)
    branch = getattr(employee, "branch", None) if employee else None
    if branch and branch.company_id:
        return int(branch.company_id)
    return 1


def _display_name(user: User) -> str:
    employee = getattr(user, "employee", None)
    if employee:
        name = " ".join(part for part in [employee.first_name, employee.last_name] if part).strip()
        if name:
            return name
    return user.email.split("@")[0]


@router.get("/search")
def search_users(
    q: str = Query("", max_length=100),
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = _user_company_id(current_user)
    term = q.strip().lower()
    users = (
        db.query(User)
        .options(joinedload(User.role), joinedload(User.employee).joinedload(Employee.branch))
        .filter(User.is_active.is_(True))
        .order_by(User.email.asc())
        .limit(250)
        .all()
    )
    items = []
    for user in users:
        if _user_company_id(user) != company_id:
            continue
        display_name = _display_name(user)
        haystack = " ".join([display_name, user.email or "", user.role.name if user.role else ""]).lower()
        if term and term not in haystack:
            continue
        items.append(
            {
                "id": user.id,
                "email": user.email,
                "displayName": display_name,
                "role": user.role.name if user.role else None,
            }
        )
        if len(items) >= limit:
            break
    return {"items": items, "total": len(items)}
