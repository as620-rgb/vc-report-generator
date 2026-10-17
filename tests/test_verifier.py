from types import SimpleNamespace
from verifier.task import verify_task


def test_verify_report_gold():
    mock_agent_output = SimpleNamespace(
        company_name="DoorDash",
        executive_summary="DoorDash (S13) operates in SF.",
        sections=[
            SimpleNamespace(title="1. Overview", content="Description..."),
            SimpleNamespace(title="2. Competition", content="Competitors..."),
            SimpleNamespace(title="3. Risks", content="Risks..."),
        ],
        risk_score=0.35,
        recommendation="INVEST",
    )

    result = verify_task(task_input={}, agent_output=mock_agent_output, workspace_path=".")
    assert result["score"] == 1.0


def test_verify_report_broken():
    mock_broken_output = SimpleNamespace(
        company_name="DoorDash",
        executive_summary="",
        sections=[],  # Missing Chapters
        risk_score=1.5,  # Risk Score for Boundary Crossing
        recommendation="MAYBE",  # Illegal enumeration
    )

    result = verify_task(task_input={}, agent_output=mock_broken_output, workspace_path=".")
    assert result["score"] == 0.0
