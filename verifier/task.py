"""
Report Generator Verifier (Task 4)
"""

from typing import Any


def verify_task(task_input: Any, agent_output: Any, workspace_path: str) -> dict:
    constraints = []

    # 1. Structural Integrity Check
    has_fields = (
        hasattr(agent_output, "company_name")
        and hasattr(agent_output, "executive_summary")
        and hasattr(agent_output, "sections")
        and hasattr(agent_output, "recommendation")
    )
    if not has_fields:
        return {
            "score": 0.0,
            "constraints": [{
                "id": "shape-check",
                "ok": False,
                "message": "agent_output missing required fields"
            }]
        }

    sections = agent_output.sections

    # ---- Constraint 1: Must include at least 3 complete chapters. ----
    ok_sections = len(sections) >= 3 and all(getattr(s, "title", None) and getattr(s, "content", None) for s in sections)
    constraints.append({
        "id": "sections-completeness",
        "ok": ok_sections,
        "message": "" if ok_sections else "Report must have at least 3 populated sections"
    })

    # ---- Constraint 2: Normative validation of investment recommendation enumerations ----
    valid_recs = {"INVEST", "PASS", "FURTHER_DD"}
    ok_rec = getattr(agent_output, "recommendation", None) in valid_recs
    constraints.append({
        "id": "valid-recommendation",
        "ok": ok_rec,
        "message": "" if ok_rec else f"Invalid recommendation: {getattr(agent_output, 'recommendation', None)}"
    })

    # ---- Constraint 3: Risk score range constraint (between 0.0 and 1.0) ----
    risk = getattr(agent_output, "risk_score", -1.0)
    ok_risk = 0.0 <= risk <= 1.0
    constraints.append({
        "id": "valid-risk-score",
        "ok": ok_risk,
        "message": "" if ok_risk else f"Risk score {risk} out of bounds [0.0, 1.0]"
    })

    score = 1.0 if all(c["ok"] for c in constraints) else 0.0
    return {
        "score": score,
        "constraints": constraints
    }
