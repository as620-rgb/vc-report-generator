"""The bundled YC companies (data/companies.json) and the memo tools."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from contract import (
    MemoInput,
    MemoOutput,
    PinOutput,
    ProfileInput,
    ProfileOutput,
    Recommendation,
    ScoreInput,
    ScoreOutput,
    WriteInput,
    WriteOutput,
)
from verifier import rules

DATA = Path(__file__).parent / "data" / "companies.json"


@cache
def directory() -> dict[str, dict]:
    return {company["slug"]: company for company in json.loads(DATA.read_text(encoding="utf-8"))}


def record(slug: str) -> dict:
    if slug not in directory():
        raise ValueError(f"no company with slug {slug!r}; the directory has {sorted(directory())}")
    return directory()[slug]


def tags(company: dict) -> tuple[str, str]:
    return company["industries"][0], company["industries"][1] if len(company["industries"]) > 1 else ""


def competitors(company: dict) -> list[str]:
    own = tags(company)
    if own[1]:
        return sorted(c["name"] for c in directory().values() if c is not company and tags(c)[1] == own[1])
    return sorted(c["name"] for c in directory().values() if c is not company and tags(c) == own)


def company_profile(request: ProfileInput, workspace: Path) -> ProfileOutput:
    company = record(request.company)
    industry, sub_industry = tags(company)
    return ProfileOutput(
        company=company["slug"],
        name=company["name"],
        tagline=company["tagline"],
        batch=company["batch"],
        batch_year=int(company["batch"].split()[-1]),
        location=company["location"],
        industry=industry,
        sub_industry=sub_industry,
        competitors=competitors(company),
    )


def score_risk(request: ScoreInput, workspace: Path) -> ScoreOutput:
    hundredths, recommendation = rules.score(request.competitors, request.years_since_batch, request.has_sub_industry)
    formula = (
        f"30 + 10 x min({request.competitors}, 4) - 2 x min({request.years_since_batch}, 15)"
        f" + {0 if request.has_sub_industry else 10} = {hundredths} hundredths, within 0 to 100"
    )
    return ScoreOutput(risk_score=hundredths / 100, recommendation=Recommendation(recommendation), formula=formula)


def write_memo(request: WriteInput, workspace: Path) -> WriteOutput:
    company = record(request.company)
    if not all(text.strip() for text in (request.overview, request.competition, request.risk)):
        raise ValueError("every section needs text")
    if any(line.startswith("#") for text in (request.overview, request.competition, request.risk) for line in text.splitlines()):
        raise ValueError("section texts may not hold headings")
    data = rules.memo_text(company["name"], request.overview, request.competition, request.risk).encode("utf-8")
    path = workspace / rules.memo_path(company["slug"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return WriteOutput(path=rules.memo_path(company["slug"]), bytes=len(data))


def pin_memo(task: MemoInput, workspace: Path) -> PinOutput:
    """The answer key: the facts the memo must report."""
    profile = company_profile(ProfileInput(company=task.company), workspace)
    if not rules.FIRST_YEAR <= task.as_of_year <= rules.LAST_YEAR or task.as_of_year < profile.batch_year:
        raise ValueError(f"as_of_year must be {rules.FIRST_YEAR} to {rules.LAST_YEAR} and not before {profile.batch_year}")
    years = task.as_of_year - profile.batch_year
    scored = score_risk(ScoreInput(len(profile.competitors), years, bool(profile.sub_industry)), workspace)
    return PinOutput(
        expected=MemoOutput(
            company=profile.company,
            name=profile.name,
            competitors=profile.competitors,
            years_since_batch=years,
            risk_score=scored.risk_score,
            recommendation=scored.recommendation,
            path=rules.memo_path(profile.company),
        ),
        batch=profile.batch,
        location=profile.location,
        sub_industry=profile.sub_industry,
        others=sorted(c["name"] for c in directory().values() if c["slug"] != profile.company),
    )
