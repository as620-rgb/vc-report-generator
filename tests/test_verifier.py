from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import (
    MemoInput,
    MemoOutput,
    PinOutput,
    ProfileInput,
    ProfileOutput,
    ScoreInput,
    ScoreOutput,
    WriteInput,
    WriteOutput,
)
from plugin.memo import company_profile, pin_memo, score_risk, write_memo


def task(company: str = "amplitude", year: int = 2026) -> MemoInput:
    return build_output({"company": company, "as_of_year": year}, MemoInput)


def key(given: MemoInput, workspace: Path) -> PinOutput:
    return build_output(plain_output(pin_memo(given, workspace)), PinOutput)


def run(given: MemoInput, workspace: Path, **sections: str) -> dict:
    """The agent's plan, scripted: three tool calls, each checked like NanoAgent checks it; returns the submission."""
    profile_in = build_output({"company": given.company}, ProfileInput)
    profile = build_output(plain_output(company_profile(profile_in, workspace)), ProfileOutput)
    assert verifier.verify_output("company_profile", profile_in, profile, str(workspace))["valid"] is True
    score_in = build_output({"competitors": len(profile.competitors), "years_since_batch": given.as_of_year - profile.batch_year,
                             "has_sub_industry": bool(profile.sub_industry)}, ScoreInput)
    scored = build_output(plain_output(score_risk(score_in, workspace)), ScoreOutput)
    assert verifier.verify_output("score_risk", score_in, scored, str(workspace))["valid"] is True
    texts = {
        "overview": f"{profile.name} ({profile.batch}) is based in {profile.location}. {profile.tagline}",
        "competition": ("It competes with " + ", ".join(profile.competitors) + ".") if profile.competitors
        else "No direct competitors in the directory.",
        "risk": f"Risk score: {scored.risk_score:.2f}\nRecommendation: {scored.recommendation.value}",
        **sections,
    }
    write_in = build_output({"company": given.company, **texts}, WriteInput)
    written = build_output(plain_output(write_memo(write_in, workspace)), WriteOutput)
    assert verifier.verify_output("write_memo", write_in, written, str(workspace))["valid"] is True
    return {"company": profile.company, "name": profile.name, "competitors": list(profile.competitors),
            "years_since_batch": score_in.years_since_batch, "risk_score": scored.risk_score,
            "recommendation": scored.recommendation.value, "path": written.path}


def check(given: MemoInput, submission: dict, workspace: Path) -> dict:
    return verifier.verify_task("write-memo", given, build_output(submission, MemoOutput), key(given, workspace), str(workspace))


def failing(verdict: dict) -> list[str]:
    return [entry["id"] for entry in verdict["details"]["constraints"] if not entry["ok"]]


def test_the_answer_key(tmp_path: Path) -> None:
    pinned = key(task(), tmp_path)
    assert plain_output(pinned.expected) == {
        "company": "amplitude", "name": "Amplitude", "competitors": ["Heap", "Segment"], "years_since_batch": 14,
        "risk_score": 0.22, "recommendation": "INVEST", "path": "memos/amplitude.md",
    }
    assert pinned.batch == "Winter 2012" and pinned.location == "San Francisco, CA, USA"


def test_approves_a_correct_memo(tmp_path: Path) -> None:
    verdict = check(task(), run(task(), tmp_path), tmp_path)
    assert verdict["valid"] is True and verdict["score"] == 1.0


def test_boundary_a_company_with_no_competitors(tmp_path: Path) -> None:
    given = task("benchling")
    submission = run(given, tmp_path)
    assert submission["competitors"] == [] and submission["risk_score"] == 0.12
    assert check(given, submission, tmp_path)["valid"] is True
    run(given, tmp_path, competition="Nobody competes.")
    assert failing(check(given, submission, tmp_path)) == ["competition-named"]


def test_boundary_the_batch_year_itself_and_a_year_before_it(tmp_path: Path) -> None:
    given = task("pagerduty", 2010)
    assert check(given, run(given, tmp_path), tmp_path)["valid"] is True
    with pytest.raises(ValueError, match="not before 2010"):
        pin_memo(task("pagerduty", 2009), tmp_path)
    assert verifier.verify_input("pin_memo", task("pagerduty", 2040))["valid"] is False


def test_rejects_wrong_facts(tmp_path: Path) -> None:
    good = run(task(), tmp_path)
    assert failing(check(task(), {**good, "risk_score": 0.3}, tmp_path)) == ["score-exact"]
    assert failing(check(task(), {**good, "recommendation": "PASS"}, tmp_path)) == ["recommendation-exact"]
    assert failing(check(task(), {**good, "years_since_batch": 15}, tmp_path)) == ["years-exact"]
    assert failing(check(task(), {**good, "competitors": ["Segment", "Heap"]}, tmp_path)) == ["competitors-exact"]
    assert failing(check(task(), {**good, "name": "amplitude"}, tmp_path)) == ["company"]


def test_rejects_a_memo_missing_facts(tmp_path: Path) -> None:
    given = task()
    submission = run(given, tmp_path, overview="Amplitude is an analytics company in San Francisco.")
    assert failing(check(given, submission, tmp_path)) == ["overview-facts"]
    run(given, tmp_path, competition="It competes with Segment.")
    assert failing(check(given, submission, tmp_path)) == ["competition-named"]
    run(given, tmp_path, risk="Risk score: 0.2\nRecommendation: INVEST")
    assert failing(check(given, submission, tmp_path)) == ["risk-figures"]


def test_rejects_a_memo_naming_a_non_competitor(tmp_path: Path) -> None:
    given = task()
    submission = run(given, tmp_path, competition="It competes with Heap, Segment and Mixpanel-like tools such as GitLab.")
    assert failing(check(given, submission, tmp_path)) == ["competition-only"]


def test_rejects_a_missing_moved_or_reordered_memo(tmp_path: Path) -> None:
    given = task()
    submission = run(given, tmp_path)
    memo = tmp_path / "memos" / "amplitude.md"
    text = memo.read_text()
    memo.write_text(text.replace("## Overview", "## Summary"))
    assert {"memo-sections", "overview-facts"} <= set(failing(check(given, submission, tmp_path)))
    memo.unlink()
    assert "memo-saved" in failing(check(given, submission, tmp_path))
    run(given, tmp_path)
    assert failing(check(given, {**submission, "path": "memo.md"}, tmp_path))[0] == "memo-saved"


def test_tool_checks(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no company"):
        company_profile(build_output({"company": "openai"}, ProfileInput), tmp_path)
    bad = build_output({"company": "amplitude", "overview": "# Title", "competition": "x", "risk": "y"}, WriteInput)
    assert verifier.verify_input("write_memo", bad)["valid"] is False
    with pytest.raises(ValueError, match="headings"):
        write_memo(bad, tmp_path)
    score_in = build_output({"competitors": 2, "years_since_batch": 14, "has_sub_industry": True}, ScoreInput)
    forged = build_output({"risk_score": 0.5, "recommendation": "FURTHER_DD", "formula": ""}, ScoreOutput)
    assert verifier.verify_output("score_risk", score_in, forged, str(tmp_path))["valid"] is False
    negative = build_output({"competitors": -1, "years_since_batch": 0, "has_sub_industry": True}, ScoreInput)
    assert verifier.verify_input("score_risk", negative)["valid"] is False


def test_rejects_a_tampered_or_missing_answer_key(tmp_path: Path) -> None:
    given = task()
    submission = run(given, tmp_path)
    pinned = plain_output(key(given, tmp_path))
    pinned["expected"]["risk_score"] = 0.9
    tampered = build_output(pinned, PinOutput)
    output = build_output(submission, MemoOutput)
    assert verifier.verify_task("write-memo", given, output, tampered, str(tmp_path))["valid"] is False
    assert verifier.verify_task("write-memo", given, output, None, str(tmp_path))["valid"] is False
