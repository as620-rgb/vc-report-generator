"""
Report Generation Tools (Task 4)
"""

from contract import (
    ReportInput,
    ReportOutput,
    InvestmentMemoSection,
)


def generate_investment_memo_tool(input_data: ReportInput) -> ReportOutput:
    co = input_data.target_company
    
    # 1. Constructing an Executive Summary
    exec_summary = (
        f"{co.company_name} ({co.batch}) operates in {co.location}. "
        f"Core value proposition: '{co.tagline}'."
    )

    # 2. Generate structured report sections
    sections = [
        InvestmentMemoSection(
            title="1. Company Overview & Positioning",
            content=f"{co.company_name} was backed by YC in {co.batch}. Website: {co.website}."
        ),
        InvestmentMemoSection(
            title="2. Competitive Landscape",
            content=f"Key identified competitors in knowledge graph: {', '.join(co.competitors) if co.competitors else 'None identified'}."
        ),
        InvestmentMemoSection(
            title="3. Investment Risks & Mitigation",
            content="Market risk is moderate. Execution risk depends on scaling go-to-market speed."
        )
    ]

# 3. Automated Risk Scoring and Investment Recommendations
    num_competitors = len(co.competitors)
    risk_score = min(0.2 + (num_competitors * 0.15), 0.85)
    
    if risk_score < 0.5:
        recommendation = "INVEST"
    elif risk_score < 0.75:
        recommendation = "FURTHER_DD"
    else:
        recommendation = "PASS"

    return ReportOutput(
        company_name=co.company_name,
        executive_summary=exec_summary,
        sections=sections,
        risk_score=round(risk_score, 2),
        recommendation=recommendation
    )
