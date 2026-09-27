from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.models import User, Organization, UserRole, Officer
from app.schemas.schemas import LoginRequest, RegisterRequest, Token, UserOut
from app.services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication header format"
        )
    
    token = parts[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token = create_access_token(subject=user.id, role=user.role.value)
    
    user_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "organization_id": user.organization_id,
        "organization_name": user.organization.name if user.organization else None,
        "officer_id": user.officer_profile.id if user.officer_profile else None,
        "officer_code": user.officer_profile.officer_code if user.officer_profile else None
    }
    
    audit_service.log_action(
        db, action="USER_LOGIN", entity_type="USER", entity_id=str(user.id), user_id=user.id
    )
    
    return {"access_token": token, "token_type": "bearer", "user": user_dict}

@router.post("/register", response_model=Token)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )
    
    org_id = None
    if req.role == UserRole.TRADER:
        org = Organization(
            name=req.organization_name or f"{req.full_name}'s Enterprise",
            trade_name=req.trade_name or req.organization_name,
            address=req.address or "Main Market, Barhi",
            state=req.state or "Jharkhand",
            district=req.district or "Hazaribagh",
            contact_email=req.email,
            contact_phone=req.phone
        )
        db.add(org)
        db.flush()
        org_id = org.id

    new_user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=req.role,
        phone=req.phone,
        organization_id=org_id
    )
    db.add(new_user)
    db.flush()

    if req.role == UserRole.LMO:
        officer = Officer(
            user_id=new_user.id,
            officer_code=f"LMO-{new_user.id:04d}",
            designation="Legal Metrology Officer",
            jurisdiction_state=req.state or "Jharkhand",
            jurisdiction_district=req.district or "Barhi / Hazaribagh"
        )
        db.add(officer)

    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=new_user.id, role=new_user.role.value)
    user_dict = {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role.value,
        "organization_id": new_user.organization_id,
        "organization_name": new_user.organization.name if new_user.organization else None,
        "officer_id": new_user.officer_profile.id if new_user.officer_profile else None
    }
    return {"access_token": token, "token_type": "bearer", "user": user_dict}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "phone": current_user.phone,
        "organization_id": current_user.organization_id,
        "organization_name": current_user.organization.name if current_user.organization else None,
        "officer_id": current_user.officer_profile.id if current_user.officer_profile else None,
        "officer_code": current_user.officer_profile.officer_code if current_user.officer_profile else None,
        "jurisdiction": f"{current_user.officer_profile.jurisdiction_district}, {current_user.officer_profile.jurisdiction_state}" if current_user.officer_profile else None
    }
