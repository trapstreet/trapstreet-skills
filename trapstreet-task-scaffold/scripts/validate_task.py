#!/usr/bin/env python3
"""Self-consistency checks for a task directory, run after build_cases.py.

Catches structural mistakes independent of the task's specific domain:
build_cases.py actually running clean, traptask.yaml's case list matching
gold.cases.json (a common copy-paste-drift bug), inputs/ not accidentally
containing anything from expected/ (a real staging mistake -- would leak
the answer), and judge.py surviving obviously-malformed input without
crashing (empty output, garbage non-JSON, one level of nesting weirdness)
if score_case() has actually been implemented.

This does NOT replace real unit tests in tests/ -- it catches a different,
narrower class of mistake that's easy to make and easy to miss by eye.

Usage:
    python3 validate_task.py <path-to-task-dir>
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def check_build_cases_runs_clean(task_dir: Path) -> list[str]:
    problems = []
    result = subprocess.run(
        [sys.executable, "build_cases.py"], cwd=task_dir, capture_output=True, text=True,
    )
    if result.returncode != 0:
        problems.append(f"build_cases.py failed:\n{result.stderr.strip()[-2000:]}")
    return problems


def check_idempotent(task_dir: Path) -> list[str]:
    """Running build_cases.py twice should produce identical output -- if
    not, something non-deterministic is leaking into inputs/expected."""
    problems = []
    result = subprocess.run(["git", "status", "--porcelain"], cwd=task_dir, capture_output=True, text=True)
    before = result.stdout
    subprocess.run([sys.executable, "build_cases.py"], cwd=task_dir, capture_output=True, text=True)
    result = subprocess.run(["git", "status", "--porcelain"], cwd=task_dir, capture_output=True, text=True)
    after = result.stdout
    if before != after:
        problems.append(
            "build_cases.py is not idempotent -- re-running it changed the working tree. "
            "Check for non-deterministic ordering (e.g. an unsorted dict/set) in the render logic."
        )
    return problems


def check_traptask_yaml_matches_gold(task_dir: Path) -> list[str]:
    problems = []
    try:
        import yaml
    except ImportError:
        return ["PyYAML not installed -- skipping traptask.yaml/gold.cases.json cross-check"]

    gold = json.loads((task_dir / "gold.cases.json").read_text())
    gold_ids = {c["id"] for c in gold["cases"]}

    traptask = yaml.safe_load((task_dir / "traptask.yaml").read_text())
    traptask_ids = {c["id"] for c in traptask.get("cases", [])}

    if gold_ids != traptask_ids:
        only_gold = gold_ids - traptask_ids
        only_traptask = traptask_ids - gold_ids
        if only_gold:
            problems.append(f"cases in gold.cases.json but missing from traptask.yaml: {sorted(only_gold)}")
        if only_traptask:
            problems.append(f"cases in traptask.yaml but missing from gold.cases.json: {sorted(only_traptask)}")
    return problems


def check_no_answer_leak_into_inputs(task_dir: Path) -> list[str]:
    """inputs/<id>/ must never contain a copy of expected/<id>/'s content --
    a real staging mistake that hands the solution the answer."""
    problems = []
    inputs_dir = task_dir / "inputs"
    expected_dir = task_dir / "expected"
    if not inputs_dir.exists() or not expected_dir.exists():
        return problems

    for case_dir in sorted(expected_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        matching_input_dir = inputs_dir / case_dir.name
        if not matching_input_dir.exists():
            continue
        for expected_file in case_dir.rglob("*"):
            if not expected_file.is_file():
                continue
            candidate = matching_input_dir / expected_file.relative_to(case_dir)
            if candidate.exists() and candidate.read_bytes() == expected_file.read_bytes():
                problems.append(
                    f"{candidate.relative_to(task_dir)} is byte-identical to "
                    f"{expected_file.relative_to(task_dir)} -- looks like expected/ content leaked into inputs/"
                )
    return problems


def check_judge_survives_malformed_input(task_dir: Path) -> list[str]:
    """If score_case() has been implemented (no longer the NotImplementedError
    stub), throw obviously-malformed input at it and confirm it degrades to
    score 0.0 rather than raising."""
    problems = []
    sys.path.insert(0, str(task_dir))
    try:
        import judge  # type: ignore
    except Exception as e:
        return [f"could not import judge.py: {e}"]

    # A minimal plausible "expected" dict -- if score_case() needs specific
    # keys it'll raise a KeyError even on well-formed stdout, which is fine
    # and expected; we're only checking robustness to malformed STDOUT here.
    expected_probe: dict = {}

    malformed_inputs = [
        ("", "empty string"),
        ("not json at all {{{", "garbage non-JSON"),
        ("null", "JSON null"),
        ("[1, 2, 3]", "JSON array instead of expected shape"),
        ('{"unexpected_key": true}', "JSON object missing expected keys"),
    ]
    for stdout, label in malformed_inputs:
        try:
            result = judge.score_case(stdout, expected_probe)
            if not isinstance(result, dict) or "score" not in result:
                problems.append(f"score_case() on {label!r} returned {result!r} -- missing 'score' key")
        except NotImplementedError:
            return []  # still a stub, nothing to check yet
        except Exception as e:
            problems.append(f"score_case() raised {type(e).__name__} on {label} input ({stdout!r}): {e}")
    return problems


CHECKS = [
    ("build_cases.py runs clean", check_build_cases_runs_clean),
    ("build_cases.py is idempotent", check_idempotent),
    ("traptask.yaml matches gold.cases.json", check_traptask_yaml_matches_gold),
    ("no answer leak into inputs/", check_no_answer_leak_into_inputs),
    ("judge.py survives malformed input", check_judge_survives_malformed_input),
]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    task_dir = Path(sys.argv[1]).expanduser().resolve()
    if not task_dir.is_dir():
        print(f"error: {task_dir} is not a directory", file=sys.stderr)
        return 1

    any_problems = False
    for name, check in CHECKS:
        problems = check(task_dir)
        if problems:
            any_problems = True
            print(f"FAIL: {name}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"OK:   {name}")

    return 1 if any_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
