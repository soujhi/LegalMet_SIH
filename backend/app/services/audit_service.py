from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog, Notification

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            old_values_json=old_values,
            new_values_json=new_values,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def send_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "INFO",
        link_url: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link_url=link_url
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

audit_service = AuditService()
