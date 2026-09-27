from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.models import Application, ApplicationStatus, ApplicationStatusHistory, Officer, User, UserRole
from app.schemas.schemas import ApplicationOut, OfficerAssign
from app.routers.auth import get_current_user
from app.services.audit_service import audit_service

router = APIRouter(prefix="/schedule", tags=["Scheduling & Officer Assignment"])

@router.get("/officers")
def list_officers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    officers = db.query(Officer).filter(Officer.is_active == True).all()
    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "name": o.user.full_name,
            "officer_code": o.officer_code,
            "designation": o.designation,
            "jurisdiction": f"{o.jurisdiction_district}, {o.jurisdiction_state}",
            "email": o.user.email,
            "phone": o.user.phone
        }
        for o in officers
    ]

@router.get("", response_model=List[ApplicationOut])
def list_scheduled(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Application).filter(
        Application.status.in_([
            ApplicationStatus.APPROVED,
            ApplicationStatus.SCHEDULED,
            ApplicationStatus.ASSIGNED,
            ApplicationStatus.FIELD_VERIFICATION
        ])
    )
    if current_user.role == UserRole.LMO and current_user.officer_profile:
        q = q.filter(Application.assigned_officer_id == current_user.officer_profile.id)
    return q.order_by(Application.scheduled_at.asc()).all()

@router.post("/assign/{application_id}", response_model=ApplicationOut)
def assign_and_schedule(
    application_id: int,
    req: OfficerAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can assign officers and schedule inspections")

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    officer = db.query(Officer).filter(Officer.id == req.officer_id).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    old_status = app.status.value
    app.assigned_officer_id = officer.id
    app.scheduled_at = req.scheduled_at
    app.status = ApplicationStatus.ASSIGNED
    app.updated_at = datetime.now(timezone.utc)

    # History
    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=ApplicationStatus.ASSIGNED.value,
        remarks=f"Assigned to {officer.user.full_name} ({officer.officer_code}) for inspection on {req.scheduled_at.strftime('%d-%b-%Y %H:%M')}. {req.remarks or ''}",
        changed_by_id=current_user.id
    )
    db.add(hist)
    db.commit()
    db.refresh(app)

    # Notifications
    audit_service.send_notification(
        db,
        user_id=officer.user_id,
        title="New Field Inspection Assigned",
        message=f"You have been assigned to verify application {app.application_number} on {req.scheduled_at.strftime('%d-%b-%Y %H:%M')}.",
        notification_type="INSPECTION_ASSIGNED",
        link_url=f"/lmo/inspections/{app.id}"
    )

    audit_service.send_notification(
        db,
        user_id=app.applicant_id,
        title="Inspection Scheduled",
        message=f"Officer {officer.user.full_name} has been assigned for field verification on {req.scheduled_at.strftime('%d-%b-%Y %H:%M')}.",
        notification_type="INSPECTION_SCHEDULED",
        link_url=f"/applications/{app.id}"
    )

    audit_service.log_action(
        db,
        action="INSPECTION_ASSIGNED",
        entity_type="APPLICATION",
        entity_id=str(app.id),
        user_id=current_user.id,
        new_values={"officer": officer.officer_code, "scheduled_at": req.scheduled_at.isoformat()}
    )

    return app
