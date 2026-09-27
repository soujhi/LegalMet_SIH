from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.models import InstrumentModel, ModelMatch, Instrument, User
from app.services.rule_engine import rule_engine
from datetime import datetime, timezone
import re

try:
    from rapidfuzz import fuzz
except ImportError:
    # Basic fallback if rapidfuzz not present
    class fuzz:
        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            s1_words = set((s1 or "").lower().split())
            s2_words = set((s2 or "").lower().split())
            if not s1_words or not s2_words:
                return 0.0
            inter = len(s1_words & s2_words)
            return (2.0 * inter / (len(s1_words) + len(s2_words))) * 100.0

class ModelReconciliationService:
    """
    Statutory Model Reconciliation Engine (PRD Section 6 & 7)
    Reconciles physical trader instrument submissions against official DoCA Model Approval catalog.
    Strictly enforces:
    - MATCH: high score >= 0.85, single clear winner -> link source PDF.
    - AMBIGUOUS: score between 0.55 and 0.85 or multiple close candidates -> flag review_required, DO NOT auto-select.
    - NO_MATCH: score < 0.55 -> do not infer compliance; flag for manual officer review.
    """

    @classmethod
    def reconcile(
        cls,
        db: Session,
        manufacturer: str,
        model_query: str,
        capacity: Optional[float] = None,
        accuracy_class: Optional[str] = None
    ) -> Dict[str, Any]:
        manuf_clean = (manufacturer or "").strip()
        model_clean = (model_query or "").strip()
        norm_input_class = rule_engine.normalize_accuracy_class(accuracy_class)

        # Retrieve all models from statutory catalog
        all_models = db.query(InstrumentModel).all()
        if not all_models:
            return {
                "status": "NO_MATCH",
                "match_score": 0.0,
                "review_required": True,
                "matched_model": None,
                "candidates": [],
                "source_pdf": None,
                "matched_fields": [],
                "unmatched_fields": ["manufacturer", "model_series", "accuracy_class"],
                "explanation": "Official DoCA Model Catalog is empty. Flagged for officer review."
            }

        candidates = []
        for m in all_models:
            # Score manufacturer similarity (0-100)
            manuf_score = fuzz.token_set_ratio(manuf_clean.lower(), (m.manufacturer or "").lower())
            
            # Score model series / brand similarity
            series_score = fuzz.token_set_ratio(model_clean.lower(), (m.model_series or "").lower())
            brand_score = fuzz.token_set_ratio(model_clean.lower(), (m.brand or "").lower())
            name_score = max(series_score, brand_score)

            # Combined textual score (weighted 40% manufacturer, 60% model)
            text_score = (manuf_score * 0.40) + (name_score * 0.60)

            # Accuracy class comparison
            model_class_norm = rule_engine.normalize_accuracy_class(m.accuracy_class)
            class_match = (norm_input_class != "UNKNOWN" and norm_input_class == model_class_norm)
            
            # Capacity range comparison
            cap_match = False
            if capacity is not None and m.max_capacity:
                min_cap = m.min_capacity or 0.0
                max_cap = m.max_capacity
                cap_match = (min_cap <= capacity <= max_cap) or (abs(capacity - max_cap) < 1e-4)

            # Bonus for metrological match
            total_score = text_score / 100.0
            if class_match:
                total_score = min(1.0, total_score + 0.05)
            if cap_match:
                total_score = min(1.0, total_score + 0.05)

            if total_score >= 0.50:
                matched_fields = []
                unmatched_fields = []
                if manuf_score >= 70:
                    matched_fields.append("manufacturer")
                else:
                    unmatched_fields.append("manufacturer")

                if name_score >= 70:
                    matched_fields.append("model_series")
                else:
                    unmatched_fields.append("model_series")

                if class_match:
                    matched_fields.append("accuracy_class")
                else:
                    unmatched_fields.append("accuracy_class")

                if cap_match:
                    matched_fields.append("capacity_range")
                else:
                    unmatched_fields.append("capacity_range")

                candidates.append({
                    "model_id": m.id,
                    "manufacturer": m.manufacturer,
                    "brand": m.brand,
                    "model_series": m.model_series,
                    "accuracy_class": m.accuracy_class,
                    "max_capacity": m.max_capacity,
                    "min_capacity": m.min_capacity,
                    "verification_scale_interval": m.verification_scale_interval,
                    "capacity_unit": m.capacity_unit or "kg",
                    "certificate_no": m.certificate_no,
                    "approval_mark": m.approval_mark,
                    "source_pdf": m.source_pdf,
                    "score": round(total_score, 3),
                    "matched_fields": matched_fields,
                    "unmatched_fields": unmatched_fields
                })

        # Sort candidates descending by score
        candidates.sort(key=lambda x: x["score"], reverse=True)

        if not candidates or candidates[0]["score"] < 0.55:
            return {
                "status": "NO_MATCH",
                "match_score": candidates[0]["score"] if candidates else 0.0,
                "review_required": True,
                "matched_model": None,
                "candidates": candidates[:3],
                "source_pdf": None,
                "matched_fields": [],
                "unmatched_fields": ["manufacturer", "model_series", "accuracy_class"],
                "explanation": (
                    f"NO MATCH: No statutory DoCA model found with sufficient confidence for "
                    f"'{manuf_clean} - {model_clean}'. Manual scrutiny required by Legal Metrology Officer."
                )
            }

        top = candidates[0]
        # Check if ambiguous (second candidate has very close score)
        if len(candidates) > 1 and (top["score"] - candidates[1]["score"]) < 0.08 and top["score"] < 0.95:
            return {
                "status": "AMBIGUOUS",
                "match_score": top["score"],
                "review_required": True,
                "matched_model": None,  # Do NOT auto-select
                "candidates": candidates[:4],
                "source_pdf": None,
                "matched_fields": top["matched_fields"],
                "unmatched_fields": top["unmatched_fields"],
                "explanation": (
                    f"AMBIGUOUS MATCH: Multiple plausible DoCA model approvals identified with close scores "
                    f"({top['score']} vs {candidates[1]['score']}). System does not auto-select. Officer selection required."
                )
            }

        # Clear high confidence match
        if top["score"] >= 0.80:
            return {
                "status": "MATCH",
                "match_score": top["score"],
                "review_required": False,
                "matched_model": top,
                "candidates": candidates[:3],
                "source_pdf": top["source_pdf"],
                "matched_fields": top["matched_fields"],
                "unmatched_fields": top["unmatched_fields"],
                "explanation": (
                    f"MATCH VERIFIED: Positively reconciled with DoCA Model Approval Certificate "
                    f"{top['certificate_no'] or top['approval_mark']} ({top['manufacturer']} {top['model_series']}). "
                    f"Source gazette certificate linked."
                )
            }
        else:
            return {
                "status": "AMBIGUOUS",
                "match_score": top["score"],
                "review_required": True,
                "matched_model": None,
                "candidates": candidates[:3],
                "source_pdf": None,
                "matched_fields": top["matched_fields"],
                "unmatched_fields": top["unmatched_fields"],
                "explanation": (
                    f"MODERATE CONFIDENCE ({top['score']}): Model candidates found but confidence below statutory auto-match threshold (0.80). "
                    f"Manual officer sign-off required."
                )
            }

    @classmethod
    def record_instrument_match(
        cls,
        db: Session,
        instrument: Instrument,
        reconciliation_result: Dict[str, Any],
        reviewer_name: Optional[str] = None
    ) -> ModelMatch:
        """
        Persists reconciliation audit record in model_matches table.
        """
        now = datetime.now(timezone.utc)
        matched_model = reconciliation_result.get("matched_model")
        
        match_record = ModelMatch(
            instrument_id=instrument.id,
            model_id=matched_model["model_id"] if matched_model else None,
            match_method="EXACT" if reconciliation_result.get("match_score", 0) >= 0.95 else "FUZZY",
            match_score=reconciliation_result.get("match_score", 0.0),
            status=reconciliation_result.get("status", "NO_MATCH"),
            review_required=reconciliation_result.get("review_required", True),
            reviewed_by=reviewer_name,
            reviewed_at=now if reviewer_name else None,
            matched_fields=reconciliation_result.get("matched_fields", []),
            unmatched_fields=reconciliation_result.get("unmatched_fields", []),
            source_pdf=reconciliation_result.get("source_pdf")
        )
        db.add(match_record)
        
        # Link instrument to approved model if clear match
        if reconciliation_result.get("status") == "MATCH" and matched_model:
            instrument.model_id = matched_model["model_id"]

        db.commit()
        db.refresh(match_record)
        return match_record

reconciliation_service = ModelReconciliationService()
