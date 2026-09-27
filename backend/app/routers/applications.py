from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.models import (
    Application, ApplicationStatus, ApplicationStatusHistory, ApplicationDocument,
    Instrument, User, UserRole
)
from app.schemas.schemas import (
    ApplicationCreate, ApplicationOut, StatusUpdate
)
from app.routers.auth import get_current_user
from app.services.audit_service import audit_service

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("", response_model=List[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = None
):
    q = db.query(Application)
    if current_user.role == UserRole.TRADER:
        q = q.filter(Application.applicant_id == current_user.id)
    elif current_user.role == UserRole.LMO:
        if current_user.officer_profile:
            q = q.filter(Application.assigned_officer_id == current_user.officer_profile.id)
    
    if status_filter:
        q = q.filter(Application.status == status_filter)
        
    return q.order_by(Application.id.desc()).all()

@router.post("", response_model=ApplicationOut)
def create_application(
    req: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inst = db.query(Instrument).filter(Instrument.id == req.instrument_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    if current_user.role == UserRole.TRADER and inst.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Instrument does not belong to your organization")
    
    # Generate statutory application number: APP-YYYYMM-XXXX
    now = datetime.now(timezone.utc)
    app_num = f"LM-APP-{now.strftime('%Y%m')}-{random.randint(10000, 99999)}"

    app = Application(
        application_number=app_num,
        instrument_id=req.instrument_id,
        applicant_id=current_user.id,
        organization_id=current_user.organization_id,
        application_type=req.application_type,
        status=ApplicationStatus.SUBMITTED,
        submitted_at=now,
        payment_status="PAID",
        payment_amount=250.0
    )
    db.add(app)
    db.flush()

    # Add initial history entry
    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status="DRAFT",
        to_status=ApplicationStatus.SUBMITTED.value,
        remarks="Application submitted by trader for scrutiny.",
        changed_by_id=current_user.id
    )
    db.add(hist)

    # Add sample default application documents if provided
    if req.documents:
        for doc in req.documents:
            app_doc = ApplicationDocument(
                application_id=app.id,
                document_type=doc.get("type", "INSTRUMENT_INVOICE"),
                file_name=doc.get("name", "document.pdf"),
                file_url=doc.get("url", "/storage/uploads/sample.pdf")
            )
            db.add(app_doc)

    db.commit()
    db.refresh(app)

    audit_service.log_action(
        db,
        action="APPLICATION_SUBMITTED",
        entity_type="APPLICATION",
        entity_id=str(app.id),
        user_id=current_user.id,
        new_values={"application_number": app.application_number}
    )

    return app

@router.get("/{id}", response_model=ApplicationOut)
def get_application(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if current_user.role == UserRole.TRADER and app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this application")
        
    return app

@router.put("/{id}/status", response_model=ApplicationOut)
def update_application_status(
    id: int,
    req: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    old_status = app.status.value
    new_status = req.status

    # Scrutiny role permissions
    if new_status in [ApplicationStatus.APPROVED, ApplicationStatus.QUERIED, ApplicationStatus.REJECTED]:
        if current_user.role not in [UserRole.ADMIN, UserRole.LMO]:
            raise HTTPException(status_code=403, detail="Only Admins/LMOs can scrutinize applications")
        app.reviewed_at = datetime.now(timezone.utc)
        app.reviewer_id = current_user.id
        app.reviewer_notes = req.remarks

    # Trader resubmit permission
    if new_status == ApplicationStatus.RESUBMITTED:
        if current_user.id != app.applicant_id:
            raise HTTPException(status_code=403, detail="Only applicant can resubmit queried applications")
        app.status = ApplicationStatus.UNDER_REVIEW

    app.status = new_status
    app.updated_at = datetime.now(timezone.utc)

    # History entry
    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=new_status.value,
        remarks=req.remarks or f"Status changed to {new_status.value}",
        changed_by_id=current_user.id
    )
    db.add(hist)
    db.commit()
    db.refresh(app)

    # Notify applicant
    audit_service.send_notification(
        db,
        user_id=app.applicant_id,
        title=f"Application {app.application_number} Update",
        message=f"Status changed to {new_status.value}. {req.remarks or ''}",
        notification_type="STATUS_UPDATE",
        link_url=f"/applications/{app.id}"
    )

    audit_service.log_action(
        db,
        action="APPLICATION_STATUS_UPDATED",
        entity_type="APPLICATION",
        entity_id=str(app.id),
        user_id=current_user.id,
        old_values={"status": old_status},
        new_values={"status": new_status.value, "remarks": req.remarks}
    )

    return app

@router.get("/{id}/timeline")
def get_application_timeline(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    history = db.query(ApplicationStatusHistory).filter(
        ApplicationStatusHistory.application_id == id
    ).order_by(ApplicationStatusHistory.created_at.asc()).all()

    return [
        {
            "id": h.id,
            "from_status": h.from_status,
            "to_status": h.to_status,
            "remarks": h.remarks,
            "changed_by": h.changed_by.full_name if h.changed_by else "System",
            "created_at": h.created_at
        }
        for h in history
    ]
