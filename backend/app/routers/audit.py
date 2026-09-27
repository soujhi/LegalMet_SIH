from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import AuditLog, User, UserRole
from app.routers.auth import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("")
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    logs = q.all()
    
    return [
        {
            "id": l.id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "user_id": l.user_id,
            "user_name": l.user.full_name if l.user else "System",
            "old_values": l.old_values_json,
            "new_values": l.new_values_json,
            "ip_address": l.ip_address,
            "created_at": l.created_at
        }
        for l in logs
    ]
