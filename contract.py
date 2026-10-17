"""
Investment Memo & Due Diligence Report Generator (Task 4)
Typed input and output declarations using nanoagent.plugin.contract standards.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from slimconfig import Output


class Tool(Enum):
    ANALYZE_COMPETITION = "analyze_competition"
    GENERATE_MEMO = "generate_memo"


class Task(Enum):
    REPORT_GENERATOR = "report-generator"


@dataclass
class TargetCompanyData(Output):
    company_name: str
    tagline: str
    batch: str
    location: str
    website: str
    competitors: list[str]


@dataclass
class ReportInput(Output):
    target_company: TargetCompanyData
    analysis_depth: Annotated[str, "Depth of report: 'summary' or 'comprehensive'"] = "comprehensive"


@dataclass
class InvestmentMemoSection(Output):
    title: str
    content: str


@dataclass
class ReportOutput(Output):
    company_name: str
    executive_summary: str
    sections: list[InvestmentMemoSection]
    risk_score: Annotated[float, "Calculated risk score between 0.0 and 1.0"]
    recommendation: Annotated[str, "'INVEST', 'PASS', or 'FURTHER_DD'"]


TOOLS = {
    Tool.GENERATE_MEMO: (ReportInput, ReportOutput),
}

TASKS = {
    Task.REPORT_GENERATOR: (ReportInput, ReportOutput),
}