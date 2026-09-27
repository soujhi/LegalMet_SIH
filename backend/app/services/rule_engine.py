from typing import Dict, Any, Optional
from app.models.models import VerificationResult

class RuleEngine:
    """
    Deterministic Legal Metrology Regulatory Rule Engine
    Complies with Legal Metrology (General) Rules, 2011 (Seventh Schedule, Part II)
    and OIML R 76-1 standards for Non-Automatic Weighing Instruments (NAWI).
    """

    @staticmethod
    def normalize_accuracy_class(raw_class: Optional[str]) -> str:
        """
        Normalize input string to canonical accuracy class token.
        Strict precedence: CLASS IIII / IV must be evaluated before CLASS III.
        """
        if not raw_class:
            return "UNKNOWN"
        cleaned = raw_class.strip().upper().replace("_", " ").replace("-", " ")
        
        # Exact canonical checks with strict order of precedence
        if "CLASS IIII" in cleaned or "CLASS IV" in cleaned or cleaned in ["IIII", "IV", "CLASS 4", "CLASS4"]:
            return "CLASS_IIII"
        if "CLASS III" in cleaned or cleaned in ["III", "CLASS 3", "CLASS3"]:
            return "CLASS_III"
        if "CLASS II" in cleaned or cleaned in ["II", "CLASS 2", "CLASS2"]:
            return "CLASS_II"
        if "CLASS I" in cleaned or cleaned in ["I", "CLASS 1", "CLASS1"]:
            return "CLASS_I"
        return "UNKNOWN"

    @classmethod
    def evaluate_test(
        cls,
        accuracy_class: Optional[str],
        capacity: Optional[float],
        scale_interval_e: Optional[float],  # in grams or base unit
        test_load: float,                   # in base unit (kg)
        observed_value: float,              # in base unit (kg)
        test_type: str = "LOAD_TEST",
        is_initial_verification: bool = False,
        unit: str = "kg",
        scale_interval_unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate error against Maximum Permissible Error (MPE).
        Enforces Seventh Schedule Part-II Table 1 and OIML R 76-1 Table 6.
        """
        # Critical Input Guard: Missing required regulatory parameters cannot auto-pass
        canonical_class = cls.normalize_accuracy_class(accuracy_class)
        if (
            canonical_class == "UNKNOWN"
            or scale_interval_e is None
            or scale_interval_e <= 0
            or capacity is None
            or capacity <= 0
        ):
            error_calc = round(observed_value - test_load, 6)
            return {
                "is_compliant": False,
                "result": VerificationResult.REVIEW_REQUIRED,
                "decision": "REVIEW_REQUIRED",
                "test_load": test_load,
                "observed_value": observed_value,
                "error_calculated": error_calc,
                "tolerance_mpe": 0.0,
                "unit": unit,
                "mpe_formula": "N/A - Review Required",
                "rule_code": "REG-REVIEW-REQUIRED",
                "is_verified_government_rule": False,
                "rule_source_reference": "Legal Metrology (General) Rules, 2011 - Input Verification Check",
                "accuracy_class": accuracy_class or "UNKNOWN",
                "scale_interval": f"{scale_interval_e} {scale_interval_unit or 'g'}",
                "comparison": f"|{error_calc:+.4f} {unit}| vs N/A (Missing Specifications)",
                "explanation": (
                    "REVIEW_REQUIRED: Missing or unrecognized critical regulatory specifications "
                    "(Accuracy Class, Verification Scale Interval 'e', or Capacity). "
                    "Deterministic compliance cannot be evaluated without statutory parameters."
                )
            }

        # Explicit Unit Normalization for Scale Interval 'e':
        # Default unit for scale interval e on NAWI scales is grams ('g').
        # If test_load and capacity are in 'kg', convert grams to kg:
        norm_scale_unit = (scale_interval_unit or "g").strip().lower()
        if unit.lower() == "kg":
            if norm_scale_unit == "g":
                e_in_kg = scale_interval_e / 1000.0
            elif norm_scale_unit == "mg":
                e_in_kg = scale_interval_e / 1000000.0
            elif norm_scale_unit == "kg":
                e_in_kg = scale_interval_e
            else:
                # Default heuristic: if e is small or in standard gram ranges, normalize by 1000
                e_in_kg = scale_interval_e / 1000.0
        elif unit.lower() == "g":
            if norm_scale_unit == "g":
                e_in_kg = scale_interval_e
            elif norm_scale_unit == "mg":
                e_in_kg = scale_interval_e / 1000.0
            elif norm_scale_unit == "kg":
                e_in_kg = scale_interval_e * 1000.0
            else:
                e_in_kg = scale_interval_e
        else:
            e_in_kg = scale_interval_e

        # Safeguard non-zero scale interval
        if e_in_kg <= 0:
            e_in_kg = 0.001

        # Verification scale interval count 'm' = test_load / e
        m_intervals = test_load / e_in_kg if e_in_kg > 0 else 0.0

        # Calculate Error: Error = Observed Value - Expected Test Load
        error_calculated = round(observed_value - test_load, 6)
        abs_error = abs(error_calculated)

        rule_code = ""
        mpe_multiplier = 1.0
        mpe_formula = ""
        is_verified_gov = True
        rule_source = "Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II (Non-Automatic Weighing Instruments) & OIML R 76-1 Table 6"

        # Apply Statutory MPE Step Functions by Canonical Class:
        if canonical_class == "CLASS_IIII":
            # Class IIII (Ordinary Accuracy)
            if m_intervals <= 50:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL4-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (in-service)"
            elif m_intervals <= 200:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL4-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (in-service)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL4-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (in-service)"

        elif canonical_class == "CLASS_III":
            # Class III (Medium Accuracy)
            if m_intervals <= 500:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL3-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (in-service)"
            elif m_intervals <= 2000:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL3-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (in-service)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL3-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (in-service)"

        elif canonical_class == "CLASS_II":
            # Class II (High Accuracy)
            if m_intervals <= 5000:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL2-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (in-service)"
            elif m_intervals <= 20000:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL2-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (in-service)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL2-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (in-service)"

        elif canonical_class == "CLASS_I":
            # Class I (Special Accuracy)
            if m_intervals <= 50000:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL1-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (in-service)"
            elif m_intervals <= 200000:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL1-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (in-service)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL1-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (in-service)"

        # Maximum Permissible Error in test unit
        tolerance_mpe = round(mpe_multiplier * e_in_kg, 6)

        is_compliant = abs_error <= (tolerance_mpe + 1e-9)
        result = VerificationResult.PASS if is_compliant else VerificationResult.FAIL
        decision_str = "PASS" if is_compliant else "FAIL"

        comparison_str = f"|{error_calculated:+.4f} {unit}| <= {tolerance_mpe:.4f} {unit}" if is_compliant else f"|{error_calculated:+.4f} {unit}| > {tolerance_mpe:.4f} {unit}"

        explanation = (
            f"Test Load: {test_load} {unit} ({round(m_intervals, 1)}e). "
            f"Observed: {observed_value} {unit} with error {error_calculated:+.4f} {unit}. "
            f"Permissible MPE limit: ±{tolerance_mpe:.4f} {unit} ({mpe_formula}). "
            f"Comparison: {comparison_str}. "
            f"Status: {'PASS - Within statutory tolerance' if is_compliant else 'FAIL - Exceeds Maximum Permissible Error'}."
        )

        return {
            "is_compliant": is_compliant,
            "result": result,
            "decision": decision_str,
            "test_load": test_load,
            "observed_value": observed_value,
            "error_calculated": error_calculated,
            "tolerance_mpe": tolerance_mpe,
            "unit": unit,
            "mpe_formula": mpe_formula,
            "rule_code": rule_code,
            "is_verified_government_rule": is_verified_gov,
            "rule_source_reference": rule_source,
            "accuracy_class": canonical_class.replace("_", " "),
            "scale_interval": f"{scale_interval_e} {norm_scale_unit}",
            "comparison": comparison_str,
            "explanation": explanation
        }

rule_engine = RuleEngine()
