"""company_profile, score_risk, write_memo and pin_memo calls."""

from pathlib import Path

from .checks import result
from .rules import FIRST_YEAR, LAST_YEAR, memo_path, score, sections


def score_problem(competitors, years, has_sub_industry, risk_score, recommendation):
    hundredths, expected = score(competitors, years, has_sub_industry)
    if abs(risk_score - hundredths / 100) > 0.0001 or recommendation != expected:
        return f"expected risk score {hundredths / 100:.2f} and {expected}, got {risk_score} and {recommendation}"
    return None


class Profile:
    @staticmethod
    def verify_input(value):
        return result(True, "input is valid") if value.company else result(False, "company is empty")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if output_value.company != input_value.company:
            return result(False, "the profile is another company's")
        if str(output_value.batch_year) != output_value.batch.split()[-1]:
            return result(False, f"batch_year {output_value.batch_year} is not the year of {output_value.batch}")
        if output_value.competitors != sorted(output_value.competitors) or output_value.name in output_value.competitors:
            return result(False, "competitors must be sorted and not hold the company itself")
        return result(True, "profile is consistent")


class Score:
    @staticmethod
    def verify_input(value):
        if value.competitors < 0 or value.years_since_batch < 0:
            return result(False, "competitors and years_since_batch must be 0 or more")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        problem = score_problem(input_value.competitors, input_value.years_since_batch, input_value.has_sub_industry,
                                output_value.risk_score, output_value.recommendation.value)
        return result(False, problem) if problem else result(True, "score follows the formula")


class Write:
    @staticmethod
    def verify_input(value):
        texts = (value.overview, value.competition, value.risk)
        if not all(text.strip() for text in texts):
            return result(False, "every section needs text")
        if any(line.startswith("#") for text in texts for line in text.splitlines()):
            return result(False, "section texts may not hold headings")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if output_value.path != memo_path(input_value.company):
            return result(False, f"the memo must be saved at {memo_path(input_value.company)}")
        path = Path(workspace) / output_value.path
        if not path.is_file():
            return result(False, f"no {output_value.path} in the workspace")
        bodies, order = sections(path.read_text(encoding="utf-8"))
        given = {"Overview": input_value.overview.strip(), "Competition": input_value.competition.strip(),
                 "Risk": input_value.risk.strip()}
        if order != list(given) or bodies != given:
            return result(False, f"{output_value.path} does not hold the sections given")
        return result(True, "memo saved")


class Pin:
    @staticmethod
    def verify_input(value):
        if not FIRST_YEAR <= value.as_of_year <= LAST_YEAR:
            return result(False, f"as_of_year must be {FIRST_YEAR} to {LAST_YEAR}")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        expected = output_value.expected
        problem = score_problem(len(expected.competitors), expected.years_since_batch, bool(output_value.sub_industry),
                                expected.risk_score, expected.recommendation.value)
        if problem or expected.years_since_batch != input_value.as_of_year - int(output_value.batch.split()[-1]):
            return result(False, problem or "years_since_batch is not as_of_year minus the batch year")
        return result(True, "answer key is consistent")
