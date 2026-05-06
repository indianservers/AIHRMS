from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import Permission, Role, User


COMMON_PERMISSIONS = [
    ("settings_view", "View platform settings", "settings"),
    ("settings_manage", "Manage platform settings", "settings"),
    ("reports_view", "View reports", "reports"),
    ("workflow_view", "View workflow inbox", "workflow"),
    ("notification_view", "View notification inbox", "notification"),
]

COMMON_ROLES = [
    {
        "name": "super_admin",
        "description": "Full system access",
        "permissions": [item[0] for item in COMMON_PERMISSIONS],
    }
]


def init_common_db(db: Session) -> None:
    perm_map = {}
    for name, description, module in COMMON_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == name).first()
        if not perm:
            perm = Permission(name=name, description=description, module=module)
            db.add(perm)
            db.flush()
        perm_map[name] = perm

    for role_data in COMMON_ROLES:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(name=role_data["name"], description=role_data["description"], is_system=True)
            db.add(role)
            db.flush()
        role.permissions = [perm_map[name] for name in role_data["permissions"] if name in perm_map]

    role = db.query(Role).filter(Role.name == "super_admin").first()
    user = db.query(User).filter(User.email == "admin@platform.local").first()
    if not user and role:
        db.add(
            User(
                email="admin@platform.local",
                hashed_password=get_password_hash("Admin@123456"),
                is_active=True,
                is_superuser=True,
                role_id=role.id,
            )
        )

    db.commit()

