from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from pathlib import Path

from app.core.database import get_db
from app.core.config import DOCA_PDFS_DIR
from app.models.models import (
    Instrument, InstrumentCategory, InstrumentModel, User, UserRole, SourceProvenance
)
from app.schemas.schemas import (
    InstrumentCreate, InstrumentOut, InstrumentCategoryOut, InstrumentModelOut,
    ModelUpdate, DataQualityStats
)
from app.routers.auth import get_current_user
from app.services.audit_service import audit_service

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
