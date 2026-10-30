# VC Memo Generator

A `nanoagent.plugin/v0001` plugin, built on the structure of NanoAgent's reference plugin,
[arxiv-source](https://github.com/zeyuyang8/arxiv-source). The agent writes a short investment memo on a YC
company: an overview, its competitors and a risk section with a rule-based score and recommendation, saved to
the workspace. Facts come from a bundled 40-company snapshot of the YC Startup Directory
(`src/plugin/data/companies.json`), so every run sees the same data offline. Every checked part of the memo
is a fact code can decide; the prose around the facts is free.

## Tools

| Tool | Does | Code |
|---|---|---|
| `company_profile` | Profiles a company: batch, location, industry, sub-industry, competitors | `src/plugin/memo.py` |
| `score_risk` | Scores risk: 30 + 10 per competitor (at most 4) − 2 per year since the batch (at most 15) + 10 without a sub-industry, within 0–100 hundredths; under 0.35 INVEST, under 0.55 FURTHER_DD, else PASS | `src/plugin/memo.py` |
| `write_memo` | Saves the Overview, Competition and Risk sections to `memos/<slug>.md` | `src/plugin/memo.py` |
| `pin_memo` | Reference tool: the facts, score and recommendation the memo must report (hidden from the agent) | `src/plugin/memo.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `write-memo` | Writes and saves the memo of one company as of a year | `agent`, with `company_profile`, `score_risk` and `write_memo`; reference `pin_memo` |

Example input: `{"company": "amplitude", "as_of_year": 2026}`: competitors Heap and Segment, 14 years since
Winter 2012, risk score 0.22, INVEST.

### Verifier

`verify_task` refuses an answer key that does not follow the formula, then runs eleven checks: `company`,
`competitors-exact`, `years-exact`, `score-exact`, `recommendation-exact`, `memo-saved`, `memo-sections`
(exactly Overview, Competition, Risk), `overview-facts` (name, batch, location), `competition-named`,
`competition-only` (no other directory company named) and `risk-figures` (`Risk score: 0.22`,
`Recommendation: INVEST`). `tests/test_rules.py` pins the formula, including both thresholds and both caps.

## Layout

```text
.
├── nanoagent.yaml   # manifest: id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output
├── src/plugin/      # the MCP server (__main__.py) and memo.py; data/ holds the company snapshot
├── tests/           # rule and verifier tests: correct, wrong, missing, malformed and boundary cases
├── ui/              # renderers (outputs drawn from their JSON Schema)
├── product/         # product page: product.yaml and icon.svg
└── verifier/        # deterministic verifier: rules.py, tools.py, task.py, checks.py
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

Publishing checks every plugin rule: push the plugin to a public GitHub repository and submit its URL
on RUSH Lab's Marketplace.
