from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_superuser, get_db, get_current_user
from app.core.security import (
    verify_password, create_access_token, create_refresh_token,
    verify_refresh_token, get_password_hash
)
from app.models.user import User
from app.models.user import Role, Permission, UserSession, MFAMethod, PasswordPolicy, LoginAttempt
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    ChangePasswordRequest, UserCreate, UserSchema,
    RoleCreate, RoleUpdate, RoleSchema, PermissionSchema,
    UserSessionCreate, UserSessionSchema, MFAMethodCreate, MFAMethodSchema,
    PasswordPolicyCreate, PasswordPolicySchema, LoginAttemptSchema,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        db.add(LoginAttempt(email=request.email, user_id=user.id if user else None, status="Failed", failure_reason="Incorrect credentials"))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        db.add(LoginAttempt(email=request.email, user_id=user.id, status="Failed", failure_reason="Account disabled"))
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    user.last_login = datetime.now(timezone.utc)
    db.add(LoginAttempt(email=request.email, user_id=user.id, status="Success"))
    db.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        role=user.role.name if user.role else None,
        is_superuser=user.is_superuser,
        employee_id=user.employee.id if user.employee else None,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_refresh_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_token = create_access_token(user.id)
    refresh_token_new = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_new,
        user_id=user.id,
        email=user.email,
        role=user.role.name if user.role else None,
        is_superuser=user.is_superuser,
        employee_id=user.employee.id if user.employee else None,
    )


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "role": current_user.role,
        "employee_id": current_user.employee.id if current_user.employee else None,
    }


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # In a stateless JWT setup, logout is client-side token removal
    # For production, implement token blacklisting with Redis
    return {"message": "Logged out successfully"}


@router.get("/users", response_model=list[UserSchema])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    return db.query(User).order_by(User.email).all()


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already exists")
    if data.role_id:
        role = db.query(Role).filter(Role.id == data.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role_id=data.role_id,
        is_superuser=data.is_superuser,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/permissions", response_model=list[PermissionSchema])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        from app.core.deps import RequirePermission
        RequirePermission("company_manage")(current_user)
    return db.query(Permission).order_by(Permission.module, Permission.name).all()


@router.get("/roles", response_model=list[RoleSchema])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        from app.core.deps import RequirePermission
        RequirePermission("company_manage")(current_user)
    return db.query(Role).order_by(Role.name).all()


@router.post("/roles", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required")
    role = Role(name=data.name, description=data.description, is_system=False)
    if data.permission_ids:
        role.permissions = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/roles/{role_id}", response_model=RoleSchema)
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    if data.permission_ids is not None:
        role.permissions = db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="System roles cannot be deleted")
    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}


@router.post("/sessions", response_model=UserSessionSchema, status_code=201)
def create_user_session(
    data: UserSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    item = UserSession(**data.model_dump(), last_seen_at=datetime.now(timezone.utc))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/sessions", response_model=list[UserSessionSchema])
def list_user_sessions(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    query = db.query(UserSession)
    if user_id:
        query = query.filter(UserSession.user_id == user_id)
    return query.order_by(UserSession.id.desc()).limit(300).all()


@router.put("/sessions/{session_id}/revoke", response_model=UserSessionSchema)
def revoke_user_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    item = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    item.status = "Revoked"
    db.commit()
    db.refresh(item)
    return item


@router.post("/mfa-methods", response_model=MFAMethodSchema, status_code=201)
def create_mfa_method(
    data: MFAMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    item = MFAMethod(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/mfa-methods/{method_id}/verify", response_model=MFAMethodSchema)
def verify_mfa_method(
    method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    item = db.query(MFAMethod).filter(MFAMethod.id == method_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="MFA method not found")
    item.is_verified = True
    item.enabled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.post("/password-policies", response_model=PasswordPolicySchema, status_code=201)
def create_password_policy(
    data: PasswordPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    if data.is_active:
        db.query(PasswordPolicy).update({PasswordPolicy.is_active: False})
    item = PasswordPolicy(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/password-policies", response_model=list[PasswordPolicySchema])
def list_password_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    return db.query(PasswordPolicy).order_by(PasswordPolicy.id.desc()).all()


@router.get("/login-attempts", response_model=list[LoginAttemptSchema])
def list_login_attempts(
    email: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    query = db.query(LoginAttempt)
    if email:
        query = query.filter(LoginAttempt.email == email)
    return query.order_by(LoginAttempt.id.desc()).limit(300).all()
