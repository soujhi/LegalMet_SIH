from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import RegulatoryRule
from app.schemas.schemas import RuleEvaluationRequest, RuleEvaluationResponse
from app.services.rule_engine import rule_engine

router = APIRouter(prefix="/rules", tags=["Regulatory Rules"])

@router.post("/evaluate", response_model=RuleEvaluationResponse)
def evaluate_rule(req: RuleEvaluationRequest):
    result = rule_engine.evaluate_test(
        accuracy_class=req.accuracy_class,
        capacity=req.capacity,
        scale_interval_e=req.verification_scale_interval,
        test_load=req.test_load,
        observed_value=req.observed_value,
        test_type=req.test_type,
        unit=req.unit
    )
    return result

@router.get("")
def list_regulatory_rules(db: Session = Depends(get_db)):
    rules = db.query(RegulatoryRule).all()
    return [
        {
            "id": r.id,
            "rule_code": r.rule_code,
            "category_id": r.category_id,
            "accuracy_class": r.accuracy_class,
            "test_type": r.test_type,
            "min_range_e": r.min_range_e,
            "max_range_e": r.max_range_e,
            "mpe_formula": r.mpe_formula,
            "mpe_multiplier": r.mpe_multiplier,
            "is_verified_government_rule": r.is_verified_government_rule,
            "rule_source_reference": r.rule_source_reference,
            "description": r.description
        }
        for r in rules
    ]
