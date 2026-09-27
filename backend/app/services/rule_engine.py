from typing import Dict, Any, Optional
from app.models.models import VerificationResult

class RuleEngine:
    """
    Deterministic Legal Metrology Regulatory Rule Engine
    Complies with Legal Metrology (General) Rules, 2011 (Seventh Schedule, Part II)
    and OIML R 76-1 standards for Non-Automatic Weighing Instruments (NAWI).
    """

    @staticmethod
    def evaluate_test(
        accuracy_class: str,
        capacity: float,
        scale_interval_e: float,  # in grams or base unit
        test_load: float,        # in kg
        observed_value: float,   # in kg
        test_type: str = "LOAD_TEST",
        is_initial_verification: bool = False,
        unit: str = "kg"
    ) -> Dict[str, Any]:
        """
        Evaluate error against Maximum Permissible Error (MPE).
        """
        # Normalization: Convert scale interval 'e' to same unit as test_load
        # Typically scale_interval_e is in grams (e.g. 5g) while test_load is in kg (e.g. 10 kg)
        e_in_unit = scale_interval_e
        if unit.lower() == "kg" and scale_interval_e > 1.0:
            # If e is given as 5 (meaning 5g) while capacity is 30 kg, e_in_kg is 0.005 kg
            e_in_kg = scale_interval_e / 1000.0
        else:
            e_in_kg = scale_interval_e

        # Number of verification scale intervals 'm' = test_load / e
        if e_in_kg <= 0:
            m_intervals = test_load * 1000
            e_in_kg = 0.001
        else:
            m_intervals = test_load / e_in_kg

        # Calculate error: Error = Observed Value - Expected Test Load
        error_calculated = round(observed_value - test_load, 6)
        abs_error = abs(error_calculated)

        rule_code = ""
        mpe_multiplier = 1.0
        mpe_formula = ""
        is_verified_gov = True
        rule_source = "Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II (Non-Automatic Weighing Instruments)"

        # Normalization of accuracy class string
        norm_class = accuracy_class.strip().upper()

        if "CLASS III" in norm_class or norm_class == "III":
            # Class III (Medium Accuracy)
            if m_intervals <= 500:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL3-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (re-verif)" if is_initial_verification else "±1.0 e (in-service/re-verif)"
            elif m_intervals <= 2000:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL3-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (re-verif)" if is_initial_verification else "±2.0 e (in-service/re-verif)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL3-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (re-verif)" if is_initial_verification else "±3.0 e (in-service/re-verif)"
                
        elif "CLASS IIII" in norm_class or "CLASS IV" in norm_class or norm_class == "IIII":
            # Class IIII (Ordinary Accuracy)
            if m_intervals <= 50:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL4-R1"
                mpe_formula = "±0.5 e (initial) / ±1.0 e (re-verif)" if is_initial_verification else "±1.0 e (in-service/re-verif)"
            elif m_intervals <= 200:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL4-R2"
                mpe_formula = "±1.0 e (initial) / ±2.0 e (re-verif)" if is_initial_verification else "±2.0 e (in-service/re-verif)"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL4-R3"
                mpe_formula = "±1.5 e (initial) / ±3.0 e (re-verif)" if is_initial_verification else "±3.0 e (in-service/re-verif)"
        elif "CLASS II" in norm_class or norm_class == "II":
            # Class II (High Accuracy)
            if m_intervals <= 5000:
                mpe_multiplier = 0.5 if is_initial_verification else 1.0
                rule_code = "LM-NAWI-CL2-R1"
                mpe_formula = "±1.0 e"
            elif m_intervals <= 20000:
                mpe_multiplier = 1.0 if is_initial_verification else 2.0
                rule_code = "LM-NAWI-CL2-R2"
                mpe_formula = "±2.0 e"
            else:
                mpe_multiplier = 1.5 if is_initial_verification else 3.0
                rule_code = "LM-NAWI-CL2-R3"
                mpe_formula = "±3.0 e"
        else:
            # Generic fallback labeled as demo rule
            mpe_multiplier = 1.0
            rule_code = "DEMO-RULE-GENERIC"
            is_verified_gov = False
            rule_source = "DEMO RULE — NOT FOR LEGAL USE (Statutory rule not configured for class)"
            mpe_formula = "±1.0 e (Demo estimate)"

        # Max Permissible Error in kg
        tolerance_mpe = round(mpe_multiplier * e_in_kg, 6)

        is_compliant = abs_error <= (tolerance_mpe + 1e-9)
        result = VerificationResult.PASS if is_compliant else VerificationResult.FAIL

        explanation = (
            f"Test Load: {test_load} {unit} ({round(m_intervals, 1)}e). "
            f"Observed: {observed_value} {unit} with error {error_calculated:+.4f} {unit}. "
            f"Permissible MPE limit: ±{tolerance_mpe} {unit} ({mpe_formula}). "
            f"Status: {'PASS - Within legal tolerance' if is_compliant else 'FAIL - Exceeds Maximum Permissible Error'}"
        )

        return {
            "is_compliant": is_compliant,
            "result": result,
            "test_load": test_load,
            "observed_value": observed_value,
            "error_calculated": error_calculated,
            "tolerance_mpe": tolerance_mpe,
            "unit": unit,
            "mpe_formula": mpe_formula,
            "rule_code": rule_code,
            "is_verified_government_rule": is_verified_gov,
            "rule_source_reference": rule_source,
            "explanation": explanation
        }

rule_engine = RuleEngine()
