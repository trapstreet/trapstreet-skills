#!/usr/bin/env python3
"""Scaffold a new trapstreet task directory: gold.cases.json, build_cases.py,
judge.py, grader.py, traptask.yaml, tests/, and README.md.

This writes the MECHANICAL parts every task shares (the manifest contracts,
the validate-then-render pipeline, the aggregation logic) with clearly
marked customization points for the parts that are genuinely task-specific
(what a case looks like, what scoring a finding correctly means). Read
../references/*.md before filling those in -- they're not optional
boilerplate, they're the actual design decisions that make a task good.

grader.py is written complete and is usually NOT customized -- its
aggregation logic (mean score, by-category breakdown, latency, cost) has
been identical across every real task in this repo. judge.py's
score_case() and build_cases.py's validate_case()/the render logic ARE
meant to be edited after generation -- they're stubbed with a TODO and a
NotImplementedError so you can't accidentally ship the stub.

Usage:
    python3 scaffold_task.py \\
        --output-dir <path to trapstreet-tasks>/tasks/<category> \\
        --task-name <task_name> \\
        --case-ids case_01 case_02 case_03   # however many you'll author
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

GOLD_CASES_JSON = '''{{
  "_doc": "Source of truth for the {task_name} task. inputs/ and expected/ are GENERATED from this file by build_cases.py -- edit here, never there.",
  "cases": [
{case_entries}
  ]
}}
'''

CASE_ENTRY_TEMPLATE = '''    {{
      "id": "{case_id}",
      "_comment": "TODO: replace this whole object with real fields for your task. Keep the id opaque (case_NN) -- see references/traptask-contract.md, Case ID naming."
    }}'''

BUILD_CASES_PY = '''"""Generate inputs/<id>/... and expected/<id>/answer.json from
gold.cases.json, validating authoring invariants first.

Run:  python3 build_cases.py
inputs/ and expected/ are GENERATED -- never edit them by hand.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD = HERE / "gold.cases.json"


def validate_case(case: dict) -> None:
    """TODO customization point. Fail loudly (raise ValueError) on
    authoring mistakes: missing fields, out-of-range values, disallowed
    licenses, duplicate structure, whatever invariants your task needs.
    See references/scoring-design.md and references/ground-truth-sourcing.md
    for what to check before you write this."""
    raise NotImplementedError(
        "validate_case() is a stub -- implement real validation for your task's fields"
    )


def build() -> None:
    data = json.loads(GOLD.read_text())
    seen_ids: set[str] = set()
    for case in data["cases"]:
        validate_case(case)
        cid = case["id"]
        if cid in seen_ids:
            raise ValueError(f"duplicate case id: {{cid}}")
        seen_ids.add(cid)

        in_dir = HERE / "inputs" / cid
        in_dir.mkdir(parents=True, exist_ok=True)
        # TODO customization point: write whatever files the solution should
        # see into in_dir, derived from `case`'s fields. Never include the
        # answer or anything that reveals it (see the case-ID-naming note
        # above, and the leakage-risk sections in references/).

        exp_dir = HERE / "expected" / cid
        exp_dir.mkdir(parents=True, exist_ok=True)
        # TODO customization point: write expected/<id>/answer.json with
        # whatever judge.py's score_case() needs to grade this case. This
        # directory is judge-only -- the solution never sees it.

    print(f"Built {{len(data['cases'])}} cases.")


if __name__ == "__main__":
    build()
'''

JUDGE_PY = '''"""Per-case judge for {task_name}.

I/O contract: reads TRAPTASK_MANIFEST (trap-cli). See
references/traptask-contract.md for the exact manifest shape.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def score_case(stdout: str, expected: dict) -> dict[str, Any]:
    """TODO customization point -- this is the actual task design. Compare
    `stdout` (the solution's raw stdout) against `expected` (the parsed
    contents of expected/<id>/answer.json) and return a dict that MUST
    include "score" (float, 0.0-1.0). Everything else is free-form
    diagnostic data.

    Read references/scoring-design.md before writing this -- in
    particular the anti-shotgun, keyword-matching, and malformed-output
    sections. Real exploits have been found in judges that skip these."""
    raise NotImplementedError(
        "score_case() is a stub -- implement real scoring for your task"
    )


def main() -> None:
    m = json.loads(os.environ["TRAPTASK_MANIFEST"])

    stdout = Path(m["run"]["stdout"]).read_text()
    exit_code = json.loads(Path(m["run"]["meta"]).read_text())["exit_code"]
    expected = json.loads((Path(m["expected_dir"]) / "answer.json").read_text())

    base = {{"id": expected.get("id")}}

    if exit_code != 0:
        print(json.dumps({{**base, "score": 0.0, "reason": f"solution exited {{exit_code}}",
                           "agent_output": stdout.strip()[:500]}}))
        return

    if not stdout.strip():
        print(json.dumps({{**base, "score": 0.0, "reason": "agent produced no output",
                           "agent_output": ""}}))
        return

    metrics = score_case(stdout, expected)
    metrics.update(base)
    metrics["agent_output"] = stdout.strip()[:500]
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
'''

GRADER_PY = '''"""Overall grader for {task_name}.

Aggregates per-case judge results (the trap-cli TRAPTASK_MANIFEST list)
into a run-level verdict. This aggregation logic is standard across every
task in this repo -- usually nothing to customize here. If your judge's
metrics dict uses a different field name than "bug_category" for its
category breakdown, update CATEGORY_FIELD below; otherwise leave this file
as-is.
"""
from __future__ import annotations

import json
import os
from collections import Counter

PASS_THRESHOLD = 0.5
CATEGORY_FIELD = "category"  # change to match your judge.py's metrics dict, or None to disable


def main() -> None:
    cases = json.loads(os.environ["TRAPTASK_MANIFEST"])

    scored = [c for c in cases if c.get("metrics") and c["metrics"].get("score") is not None]
    skipped = [c for c in cases if not c.get("metrics") or c["metrics"].get("score") is None]

    accuracy = sum(c["metrics"]["score"] for c in scored) / len(scored) if scored else 0.0

    by_category_pct = {{}}
    if CATEGORY_FIELD:
        by_category_score: Counter[str] = Counter()
        by_category_total: Counter[str] = Counter()
        for c in scored:
            cat = c["metrics"].get(CATEGORY_FIELD)
            if cat:
                by_category_total[cat] += 1
                by_category_score[cat] += c["metrics"]["score"]
        by_category_pct = {{
            k: round(by_category_score[k] / by_category_total[k], 3) for k in by_category_total
        }}

    durations = [c.get("duration", 0.0) for c in cases if c.get("duration") is not None]
    if durations:
        ds = sorted(durations)
        latency_ms_median = round(ds[len(ds) // 2] * 1000, 1)
        latency_ms_p95 = round(ds[int(0.95 * len(ds))] * 1000, 1) if len(ds) > 1 else latency_ms_median
        latency_ms_total = round(sum(ds) * 1000, 1)
    else:
        latency_ms_median = latency_ms_p95 = latency_ms_total = 0.0

    case_costs = [
        c["cost"]["cost_usd"]
        for c in cases
        if isinstance(c.get("cost"), dict) and c["cost"].get("cost_usd") is not None
    ]
    cost_usd_total = round(sum(case_costs), 4) if case_costs else None

    n_passed = sum(1 for c in scored if c["metrics"]["score"] == 1.0)

    passed = bool(scored) and accuracy >= PASS_THRESHOLD

    print(json.dumps({{
        "passed": passed,
        "score": round(accuracy, 3),
        "n_passed": n_passed,
        "n_total": len(cases),
        "n_scored": len(scored),
        "n_skipped_no_gold": len(skipped),
        "threshold": PASS_THRESHOLD,
        "by_category": by_category_pct,
        "latency_ms_median": latency_ms_median,
        "latency_ms_p95": latency_ms_p95,
        "latency_ms_total": latency_ms_total,
        "cost_usd_total": cost_usd_total,
    }}))


if __name__ == "__main__":
    main()
'''

TRAPTASK_YAML = """dirs:
  inputs: inputs/
  expected: expected/

cases:
{case_entries}

judge:
  cmd: python3 judge.py

grader:
  cmd: python3 grader.py
"""

TRAPTASK_CASE_TEMPLATE = """- id: {case_id}
  description: "TODO: one-line human summary of what this case tests"
  tags: [TODO_domain, TODO_subcategory]"""

TEST_BUILD_PY = '''# tests/test_build.py
import sys, pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_cases  # noqa: E402


def test_validate_case_is_implemented():
    """This fails until you replace build_cases.validate_case()'s
    NotImplementedError stub with real validation logic. Once you do,
    replace this test with real cases: valid-case-passes, and one
    test per invariant validate_case() is supposed to catch."""
    with pytest.raises(NotImplementedError):
        build_cases.validate_case({})
'''

TEST_JUDGE_PY = '''# tests/test_judge.py
import sys, pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import judge  # noqa: E402


def test_score_case_is_implemented():
    """This fails until you replace judge.score_case()'s
    NotImplementedError stub with real scoring logic. Once you do, replace
    this test with real cases -- see references/scoring-design.md for the
    known-exploit cases you should specifically test for (substring vs.
    word-boundary matching, malformed JSON, Infinity/NaN, anti-shotgun)."""
    with pytest.raises(NotImplementedError):
        judge.score_case("", {})
'''

README_MD = """# {task_name}

TODO: one-paragraph description of what this task tests and why.

## Why this task

TODO: what real-world capability does this measure? Why does it matter?
See the trapstreet-task-scaffold skill's references/ground-truth-sourcing.md
for the positioning constraints this should satisfy (a separate repo from
this task -- no reliable relative path between the two, reference by name).

## Input / output contract

TODO: describe exactly what the solution receives (inputs/<id>/...) and
what it must print to stdout.

## Scoring

TODO: describe score_case()'s logic in plain language, and state any known
limitations plainly (see references/scoring-design.md's "known ceiling"
framing for keyword matching, if applicable).

## Sources & licensing

TODO: if any case uses real external material, list source + license here,
matching the table format used by other tasks in this repo.

## Run

```bash
python3 build_cases.py                 # (re)generate cases
python3 -m pytest tests/ -v            # unit tests
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", required=True, help="parent category dir, e.g. .../tasks/<category>")
    parser.add_argument("--task-name", required=True)
    parser.add_argument("--case-ids", nargs="+", required=True)
    args = parser.parse_args()

    task_dir = Path(args.output_dir).expanduser() / args.task_name
    task_dir.mkdir(parents=True, exist_ok=False)
    (task_dir / "tests").mkdir()

    case_entries = ",\n".join(CASE_ENTRY_TEMPLATE.format(case_id=c) for c in args.case_ids)
    (task_dir / "gold.cases.json").write_text(
        GOLD_CASES_JSON.format(task_name=args.task_name, case_entries=case_entries)
    )
    (task_dir / "build_cases.py").write_text(BUILD_CASES_PY)
    (task_dir / "judge.py").write_text(JUDGE_PY.format(task_name=args.task_name))
    (task_dir / "grader.py").write_text(GRADER_PY.format(task_name=args.task_name))

    traptask_entries = "\n".join(TRAPTASK_CASE_TEMPLATE.format(case_id=c) for c in args.case_ids)
    (task_dir / "traptask.yaml").write_text(TRAPTASK_YAML.format(case_entries=traptask_entries))

    (task_dir / "tests" / "test_build.py").write_text(TEST_BUILD_PY)
    (task_dir / "tests" / "test_judge.py").write_text(TEST_JUDGE_PY)
    (task_dir / "README.md").write_text(README_MD.format(task_name=args.task_name))

    print(f"Task scaffold written to {task_dir}")
    print()
    print("Next steps -- in this order, since later steps depend on earlier ones:")
    print("  1. Read ../references/ground-truth-sourcing.md and legal-ip-checklist.md")
    print("     BEFORE sourcing any real case material -- decide local-only vs. public now.")
    print("  2. Fill in real cases in gold.cases.json (replace the placeholder case objects).")
    print("  3. Implement build_cases.py's validate_case() and the two render TODOs.")
    print("  4. Read ../references/scoring-design.md, then implement judge.py's score_case().")
    print("  5. Fill in traptask.yaml's description/tags per case.")
    print("  6. Replace the stub tests in tests/ with real coverage -- exact hit, near-miss,")
    print("     malformed input, and any exploit class from scoring-design.md that applies.")
    print("  7. python3 build_cases.py && python3 -m pytest tests/ -v")
    print("  8. Run scripts/validate_task.py (in this skill) for an end-to-end self-consistency check.")
    print("  9. Fill in README.md, including the sources/licensing table if using real material.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
