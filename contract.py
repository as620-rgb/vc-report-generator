"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    COMPANY_PROFILE = "company_profile"
    SCORE_RISK = "score_risk"
    WRITE_MEMO = "write_memo"
    PIN_MEMO = "pin_memo"


class Task(Enum):
    WRITE_MEMO = "write-memo"


class Recommendation(Enum):
    INVEST = "INVEST"
    FURTHER_DD = "FURTHER_DD"
    PASS = "PASS"


SLUG = "A company's directory slug, e.g. amplitude"
COMPETITORS = "The names of its competitors, sorted"


@dataclass
class MemoInput(Output):
    company: Annotated[str, SLUG]
    as_of_year: Annotated[int, "The year the memo is written in, 2005 to 2035, not before the company's batch year"]


@dataclass
class MemoOutput(Output):
    company: Annotated[str, SLUG]
    name: Annotated[str, "The company's name"]
    competitors: Annotated[list[str], COMPETITORS]
    years_since_batch: Annotated[int, "as_of_year minus the batch year"]
    risk_score: Annotated[float, "The score score_risk returned"]
    recommendation: Annotated[Recommendation, "The recommendation score_risk returned"]
    path: Annotated[str, "The memo file, relative to the workspace, as write_memo returned it"]


@dataclass
class ProfileInput(Output):
    company: Annotated[str, SLUG]


@dataclass
class ProfileOutput(Output):
    company: str
    name: str
    tagline: str
    batch: Annotated[str, "e.g. Winter 2012"]
    batch_year: int
    location: str
    industry: str
    sub_industry: Annotated[str, "Empty when the company has only one industry tag"]
    competitors: Annotated[
        list[str],
        "The other directory companies with the same sub-industry, or, for a company without one, with the same "
        "industry and no sub-industry; names sorted",
    ]


@dataclass
class ScoreInput(Output):
    competitors: Annotated[int, "How many competitors the company has, 0 or more"]
    years_since_batch: Annotated[int, "The memo's year minus the batch year, 0 or more"]
    has_sub_industry: Annotated[bool, "Whether the company has a sub-industry"]


@dataclass
class ScoreOutput(Output):
    risk_score: Annotated[float, "0.00 to 1.00, two decimals"]
    recommendation: Recommendation
    formula: Annotated[str, "How the score was computed"]


@dataclass
class WriteInput(Output):
    company: Annotated[str, SLUG]
    overview: Annotated[str, "The Overview section's text"]
    competition: Annotated[str, "The Competition section's text"]
    risk: Annotated[str, "The Risk section's text"]


@dataclass
class WriteOutput(Output):
    path: Annotated[str, "The memo file, relative to the workspace: memos/<slug>.md"]
    bytes: int


@dataclass
class PinOutput(Output):
    expected: Annotated[MemoOutput, "The facts the memo must report"]
    batch: str
    location: str
    sub_industry: Annotated[str, "Empty when the company has only one industry tag"]
    others: Annotated[list[str], "Every other directory company's name"]


TOOLS = {
    Tool.COMPANY_PROFILE: (ProfileInput, ProfileOutput),
    Tool.SCORE_RISK: (ScoreInput, ScoreOutput),
    Tool.WRITE_MEMO: (WriteInput, WriteOutput),
    Tool.PIN_MEMO: (MemoInput, PinOutput),
}
TASKS = {Task.WRITE_MEMO: (MemoInput, MemoOutput)}
