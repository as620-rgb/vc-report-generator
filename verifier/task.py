"""write-memo: the reported facts against the answer key, and the saved memo's sections against the facts."""

from pathlib import Path

from .checks import constraint, result, verdict
from .rules import NO_COMPETITORS, SECTIONS, mentions, sections
from .tools import Pin


def verify_task(arguments, output, reference, workspace):
    if reference is None:
        return result(False, "no answer key was pinned")
    if not Pin.verify_output(arguments, reference, workspace)["valid"]:
        return result(False, "the pinned answer key is not consistent")
    want = reference.expected
    score_text = f"Risk score: {want.risk_score:.2f}"
    recommendation_text = f"Recommendation: {want.recommendation.value}"

    file_problem = None
    bodies, order = {}, []
    if output.path != want.path:
        file_problem = f"path must be {want.path}"
    elif not (Path(workspace) / want.path).is_file():
        file_problem = f"no {want.path} in the workspace"
    else:
        bodies, order = sections((Path(workspace) / want.path).read_text(encoding="utf-8"))
    overview, competition, risk = (bodies.get(name, "") for name in SECTIONS)

    facts_missing = [fact for fact in (want.name, reference.batch, reference.location) if not mentions(overview, fact)]
    named = [name for name in reference.others if mentions(competition, name)]
    unnamed = [name for name in want.competitors if name not in named]
    wrongly_named = [name for name in named if name not in want.competitors]
    if not want.competitors and NO_COMPETITORS not in competition:
        unnamed = [NO_COMPETITORS]
    risk_missing = [text for text in (score_text, recommendation_text) if text not in risk]

    return verdict([
        constraint("company", "company and name are the task's", (output.company, output.name) == (want.company, want.name),
                   [want.company, want.name], [output.company, output.name]),
        constraint("competitors-exact", "competitors are exactly the profile's, sorted",
                   list(output.competitors) == list(want.competitors), want.competitors, output.competitors),
        constraint("years-exact", "years_since_batch is as_of_year minus the batch year",
                   output.years_since_batch == want.years_since_batch, want.years_since_batch, output.years_since_batch),
        constraint("score-exact", "risk_score follows the formula", abs(output.risk_score - want.risk_score) < 0.0001,
                   want.risk_score, output.risk_score),
        constraint("recommendation-exact", "the recommendation follows the score",
                   output.recommendation == want.recommendation, want.recommendation.value, output.recommendation.value),
        constraint("memo-saved", f"the memo is saved at {want.path}", file_problem is None, want.path, output.path,
                   file_problem or ""),
        constraint("memo-sections", "the memo has exactly the sections Overview, Competition and Risk, in order",
                   order == list(SECTIONS), list(SECTIONS), order),
        constraint("overview-facts", "Overview names the company, its batch and its location", not facts_missing,
                   [], facts_missing, f"Overview does not name {facts_missing}"),
        constraint("competition-named", "Competition names every competitor (or says there are none)", not unnamed,
                   [], unnamed, f"Competition does not name {unnamed}"),
        constraint("competition-only", "Competition names no directory company that is not a competitor",
                   not wrongly_named, [], wrongly_named, f"Competition names non-competitors {wrongly_named}"),
        constraint("risk-figures", f'Risk states "{score_text}" and "{recommendation_text}"', not risk_missing,
                   [score_text, recommendation_text], risk_missing, f"Risk does not state {risk_missing}"),
    ])
