"""The scoring and memo rules: pure standard library, so both the tools and the sandboxed verifier use them."""

import re

FIRST_YEAR, LAST_YEAR = 2005, 2035
SECTIONS = ("Overview", "Competition", "Risk")
NO_COMPETITORS = "No direct competitors in the directory."
HEADING = re.compile(r"^## (.+)$", re.MULTILINE)


def score(competitors, years_since_batch, has_sub_industry):
    """(risk score in hundredths, recommendation): 30 + 10 per competitor (at most 4) - 2 per year since the
    batch (at most 15) + 10 without a sub-industry, kept within 0 to 100."""
    if competitors < 0 or years_since_batch < 0:
        raise ValueError("competitors and years_since_batch must be 0 or more")
    hundredths = 30 + 10 * min(competitors, 4) - 2 * min(years_since_batch, 15) + (0 if has_sub_industry else 10)
    hundredths = max(0, min(100, hundredths))
    recommendation = "INVEST" if hundredths < 35 else "FURTHER_DD" if hundredths < 55 else "PASS"
    return hundredths, recommendation


def memo_path(slug):
    return f"memos/{slug}.md"


def memo_text(name, overview, competition, risk):
    return f"# Investment memo: {name}\n\n## Overview\n\n{overview.strip()}\n\n## Competition\n\n{competition.strip()}\n\n## Risk\n\n{risk.strip()}\n"


def sections(text):
    """{heading: body} of a memo's ## sections, and the headings in order."""
    marks = list(HEADING.finditer(text))
    bodies = {}
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        bodies[mark.group(1).strip()] = text[mark.end() : end].strip()
    return bodies, [mark.group(1).strip() for mark in marks]


def mentions(text, name):
    """Whether text names name as a whole phrase, matching case."""
    return re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text) is not None
