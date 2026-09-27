from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.config import DOCA_PDFS_DIR
from app.models.models import (
    Instrument, InstrumentCategory, InstrumentModel, User, UserRole, SourceProvenance, ModelMatch
)
from app.schemas.schemas import (
    InstrumentCreate, InstrumentOut, InstrumentCategoryOut, InstrumentModelOut,
    ModelUpdate, DataQualityStats, ReconcileRequest, ReconcileResponse, MatchReviewRequest
)
from app.routers.auth import get_current_user
from app.services.audit_service import audit_service
from app.services.reconciliation_service import reconciliation_service

router = APIRouter(prefix="/instruments", tags=["Instruments"])

@router.get("/categories", response_model=List[InstrumentCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(InstrumentCategory).all()

@router.get("/models", response_model=List[InstrumentModelOut])
def list_models(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    accuracy_class: Optional[str] = None,
    manufacturer: Optional[str] = None,
    brand: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(InstrumentModel)
    if category_id:
        query = query.filter(InstrumentModel.category_id == category_id)
    if accuracy_class:
        query = query.filter(InstrumentModel.accuracy_class == accuracy_class)
    if manufacturer:
        query = query.filter(InstrumentModel.manufacturer.ilike(f"%{manufacturer}%"))
    if brand:
        query = query.filter(InstrumentModel.brand.ilike(f"%{brand}%"))
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                InstrumentModel.model_series.ilike(search_pattern),
                InstrumentModel.manufacturer.ilike(search_pattern),
                InstrumentModel.brand.ilike(search_pattern),
                InstrumentModel.approval_mark.ilike(search_pattern),
                InstrumentModel.certificate_no.ilike(search_pattern),
                InstrumentModel.equipment.ilike(search_pattern),
            )
        )
    return query.order_by(InstrumentModel.id.asc()).offset(skip).limit(limit).all()

@router.get("/models/data-quality", response_model=DataQualityStats)
def get_data_quality_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(InstrumentModel).count()
    doca_count = db.query(InstrumentModel).filter(InstrumentModel.source_provenance == SourceProvenance.DOCA_MODEL_APPROVAL).count()
    ocr_count = db.query(InstrumentModel).filter(InstrumentModel.source_provenance == SourceProvenance.OCR).count()
    manual_count = db.query(InstrumentModel).filter(InstrumentModel.source_provenance == SourceProvenance.MANUAL).count()
    verified_count = db.query(InstrumentModel).filter(InstrumentModel.manual_verified == True).count()
    high_conf_count = db.query(InstrumentModel).filter(InstrumentModel.extraction_confidence >= 90.0).count()

    # Missing fields counts across all models
    missing_lc_model = db.query(InstrumentModel).filter(
        or_(InstrumentModel.load_cell_model == None, InstrumentModel.load_cell_model == "")
    ).count()
    missing_approval_coverage = db.query(InstrumentModel).filter(
        or_(InstrumentModel.approval_coverage == None, InstrumentModel.approval_coverage == "")
    ).count()
    missing_checksum = db.query(InstrumentModel).filter(
        or_(InstrumentModel.checksum == None, InstrumentModel.checksum == "")
    ).count()
    missing_software_ver = db.query(InstrumentModel).filter(
        or_(InstrumentModel.software_version == None, InstrumentModel.software_version == "")
    ).count()
    missing_sealing = db.query(InstrumentModel).filter(
        or_(InstrumentModel.sealing_details == None, InstrumentModel.sealing_details == "")
    ).count()

    # Accuracy class distribution
    acc_classes = db.query(InstrumentModel.accuracy_class, func.count(InstrumentModel.id)).group_by(InstrumentModel.accuracy_class).all()
    acc_distribution = {ac: count for ac, count in acc_classes if ac}

    return DataQualityStats(
        total_models=total,
        doca_models=doca_count,
        ocr_models=ocr_count,
        manual_models=manual_count,
        manual_verified_count=verified_count,
        high_confidence_count=high_conf_count,
        missing_fields_summary={
            "load_cell_model": missing_lc_model,
            "approval_coverage": missing_approval_coverage,
            "checksum": missing_checksum,
            "software_version": missing_software_ver,
            "sealing_details": missing_sealing
        },
        accuracy_class_distribution=acc_distribution
    )

@router.get("/models/{id}", response_model=InstrumentModelOut)
def get_model_details(id: int, db: Session = Depends(get_db)):
    model = db.query(InstrumentModel).filter(InstrumentModel.id == id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Instrument Model not found")
    return model

@router.put("/models/{id}", response_model=InstrumentModelOut)
def update_model_details(
    id: int,
    req: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.CONTROLLER]:
        raise HTTPException(status_code=403, detail="Only Admin or Controller can update model catalog")

    model = db.query(InstrumentModel).filter(InstrumentModel.id == id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Instrument Model not found")

    old_vals = {}
    new_vals = {}
    for key, val in req.model_dump(exclude_unset=True).items():
        old_val = getattr(model, key, None)
        if old_val != val:
            old_vals[key] = str(old_val)
            new_vals[key] = str(val)
            setattr(model, key, val)

    db.commit()
    db.refresh(model)

    audit_service.log_action(
        db,
        action="MODEL_CATALOG_UPDATED",
        entity_type="INSTRUMENT_MODEL",
        entity_id=str(model.id),
        user_id=current_user.id,
        old_values=old_vals,
        new_values=new_vals
    )

    return model

@router.get("/models/{id}/source-pdf")
def get_model_source_pdf(id: int, db: Session = Depends(get_db)):
    model = db.query(InstrumentModel).filter(InstrumentModel.id == id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Instrument Model not found")
    
    if not model.source_pdf:
        raise HTTPException(status_code=404, detail="No source PDF associated with this model")

    pdf_filename = Path(model.source_pdf).name
    pdf_path = DOCA_PDFS_DIR / pdf_filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Source PDF file '{pdf_filename}' not found on server")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename
    )

@router.get("", response_model=List[InstrumentOut])
def list_instruments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Instrument)
    if current_user.role == UserRole.TRADER:
        query = query.filter(Instrument.organization_id == current_user.organization_id)
    return query.order_by(Instrument.id.desc()).all()

@router.post("", response_model=InstrumentOut)
def create_instrument(
    req: InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to register instruments"
        )
    
    # Check duplicate serial number in organization
    existing = db.query(Instrument).filter(
        Instrument.serial_number == req.serial_number,
        Instrument.organization_id == current_user.organization_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An instrument with serial number '{req.serial_number}' is already registered in your enterprise."
        )

    inst = Instrument(
        organization_id=current_user.organization_id,
        category_id=req.category_id,
        model_id=req.model_id,
        serial_number=req.serial_number,
        asset_number=req.asset_number,
        capacity=req.capacity,
        unit=req.unit,
        accuracy_class=req.accuracy_class,
        verification_scale_interval=req.verification_scale_interval,
        location=req.location or "Barhi Market Storefront",
        status="ACTIVE",
        source_provenance=SourceProvenance.MANUAL
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)

    audit_service.log_action(
        db,
        action="INSTRUMENT_REGISTERED",
        entity_type="INSTRUMENT",
        entity_id=str(inst.id),
        user_id=current_user.id,
        new_values={"serial_number": inst.serial_number, "capacity": inst.capacity}
    )

    return inst

@router.get("/{id}", response_model=InstrumentOut)
def get_instrument(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if current_user.role == UserRole.TRADER and inst.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this instrument")
    return inst

@router.put("/{id}", response_model=InstrumentOut)
def update_instrument(
    id: int,
    req: InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if current_user.role == UserRole.TRADER and inst.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this instrument")
    
    inst.category_id = req.category_id
    inst.model_id = req.model_id
    inst.serial_number = req.serial_number
    inst.asset_number = req.asset_number
    inst.capacity = req.capacity
    inst.unit = req.unit
    inst.accuracy_class = req.accuracy_class
    inst.verification_scale_interval = req.verification_scale_interval
    if req.location:
        inst.location = req.location

    db.commit()
    db.refresh(inst)
    return inst

# ----------------- PRD Section 7: Official Model Reconciliation Endpoints -----------------

@router.post("/reconcile", response_model=ReconcileResponse)
def reconcile_model_query(
    req: ReconcileRequest,
    db: Session = Depends(get_db)
):
    """
    Statutory Model Reconciliation Lookup.
    Compares Manufacturer + Model against the 451 DoCA Gazette records.
    Returns MATCH, AMBIGUOUS, or NO_MATCH.
    """
    result = reconciliation_service.reconcile(
        db=db,
        manufacturer=req.manufacturer,
        model_query=req.model_query,
        capacity=req.capacity,
        accuracy_class=req.accuracy_class
    )
    return result

@router.post("/{id}/reconcile")
def reconcile_instrument(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reconciles a registered physical instrument against the DoCA catalog and persists an audit match record.
    """
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # If instrument has an existing model, use it as query; otherwise use category/asset tags
    query_model = inst.model.model_series if inst.model else (inst.asset_number or "")
    query_manuf = inst.model.manufacturer if inst.model else ""

    result = reconciliation_service.reconcile(
        db=db,
        manufacturer=query_manuf,
        model_query=query_model,
        capacity=inst.capacity,
        accuracy_class=inst.accuracy_class
    )

    match_record = reconciliation_service.record_instrument_match(
        db=db,
        instrument=inst,
        reconciliation_result=result,
        reviewer_name=current_user.full_name if current_user.role in [UserRole.ADMIN, UserRole.LMO] else None
    )

    return {
        "instrument_id": inst.id,
        "match_id": match_record.id,
        "status": match_record.status,
        "match_score": match_record.match_score,
        "review_required": match_record.review_required,
        "model_id": match_record.model_id,
        "source_pdf": match_record.source_pdf,
        "reconciliation": result
    }

@router.get("/{id}/matches")
def get_instrument_matches(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all model reconciliation audit records for an instrument.
    """
    inst = db.query(Instrument).filter(Instrument.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    matches = db.query(ModelMatch).filter(ModelMatch.instrument_id == id).order_by(ModelMatch.id.desc()).all()
    return [
        {
            "id": m.id,
            "instrument_id": m.instrument_id,
            "model_id": m.model_id,
            "match_method": m.match_method,
            "match_score": m.match_score,
            "status": m.status,
            "review_required": m.review_required,
            "reviewed_by": m.reviewed_by,
            "reviewed_at": m.reviewed_at,
            "matched_fields": m.matched_fields,
            "unmatched_fields": m.unmatched_fields,
            "source_pdf": m.source_pdf,
            "model_details": {
                "manufacturer": m.model.manufacturer,
                "model_series": m.model.model_series,
                "approval_mark": m.model.approval_mark,
                "accuracy_class": m.model.accuracy_class
            } if m.model else None
        }
        for m in matches
    ]

@router.put("/matches/{match_id}/review")
def review_model_match(
    match_id: int,
    req: MatchReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Officer review / sign-off on ambiguous or no-match model reconciliations.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LMO]:
        raise HTTPException(status_code=403, detail="Only Legal Metrology Officers or Admins can review model matches")

    match = db.query(ModelMatch).filter(ModelMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match record not found")

    if req.model_id:
        model = db.query(InstrumentModel).filter(InstrumentModel.id == req.model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Target model approval not found")
        match.model_id = model.id
        match.source_pdf = model.source_pdf
        # Also assign to instrument
        match.instrument.model_id = model.id

    match.status = req.status
    match.review_required = False
    match.reviewed_by = current_user.full_name
    match.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    audit_service.log_action(
        db,
        action="MODEL_MATCH_REVIEWED",
        entity_type="MODEL_MATCH",
        entity_id=str(match.id),
        user_id=current_user.id,
        new_values={"status": match.status, "model_id": match.model_id, "reviewed_by": match.reviewed_by}
    )

    return {
        "success": True,
        "match_id": match.id,
        "status": match.status,
        "review_required": match.review_required,
        "model_id": match.model_id,
        "reviewed_by": match.reviewed_by
    }

