# Task contract — authoritative, verified against a real shipped task

Every task in `trapstreet-tasks` follows the same file layout and I/O
contract, regardless of domain. This is the mechanical part -- get this
right once via the scaffold script and never re-derive it by hand.

```
tasks/<category>/<task_name>/
├── gold.cases.json      # source of truth. Edit here, NEVER in inputs/expected.
├── build_cases.py        # validates gold.cases.json, generates inputs/ + expected/
├── judge.py               # scores ONE case's run against its expected answer
├── grader.py               # aggregates all cases' judge results into a run verdict
├── traptask.yaml            # case list + tags + judge/grader command declarations
├── inputs/<case_id>/...       # GENERATED -- what the solution actually sees
├── expected/<case_id>/...      # GENERATED -- judge-only, solution never sees this
├── tests/test_build.py          # unit tests for build_cases.py's validation logic
├── tests/test_judge.py           # unit tests for judge.py's scoring logic
└── README.md                      # I/O contract, scoring explanation, sources/licensing
```

## The manifest contracts (three different env vars, don't confuse them)

| Stage | Env var | Shape |
|---|---|---|
| Solution | `TRAP_MANIFEST` | `{"inputs_dir": "...", "outputs_dir": "..."}` |
| Judge (per-case) | `TRAPTASK_MANIFEST` | `{"inputs_dir", "expected_dir", "outputs_dir", "run": {"stdout": "<path>", "stderr": "<path>", "meta": "<path>"}}` -- `meta` is a JSON file with `{"exit_code": int, "duration": float}` |
| Grader (run-level) | `TRAPTASK_MANIFEST` | a JSON **list** of `{"case_id", "exit_code", "duration", "metrics", "cost"}` -- `metrics` is whatever `judge.py` printed for that case; `cost` is `{"cost_usd": float, "by_model": [...]}` or `None` |

Judge and grader share the `TRAPTASK_MANIFEST` name but get a different
shape (a dict for judge, a list for grader) -- read from the right key.

## judge.py -- the shape every real judge follows

```python
def score_case(stdout: str, expected: dict) -> dict:
    """THE CUSTOMIZATION POINT. Compare stdout against expected, return a
    dict that MUST include "score" (0.0-1.0). Everything else in this dict
    is free-form diagnostic data (shown in the run UI, not graded)."""
    ...

def main() -> None:
    m = json.loads(os.environ["TRAPTASK_MANIFEST"])
    stdout = Path(m["run"]["stdout"]).read_text()
    exit_code = json.loads(Path(m["run"]["meta"]).read_text())["exit_code"]
    expected = json.loads((Path(m["expected_dir"]) / "answer.json").read_text())

    if exit_code != 0:
        print(json.dumps({"score": 0.0, "reason": f"solution exited {exit_code}"}))
        return
    if not stdout.strip():
        print(json.dumps({"score": 0.0, "reason": "agent produced no output"}))
        return

    metrics = score_case(stdout, expected)
    print(json.dumps(metrics))

if __name__ == "__main__":
    main()
```

`score_case()` is where the real design work happens -- see
`scoring-design.md`. Everything else above is boilerplate; the scaffold
script writes it for you.

## grader.py -- genuinely reusable as-is

Unlike judge.py, grader.py's aggregation logic has been byte-identical
across every task in this repo (mean score, `n_passed`, per-category
breakdown, latency percentiles, total cost). The scaffold script writes a
complete, working `grader.py` -- there's usually nothing to customize here
unless your task's `metrics` dict uses a field name other than
`bug_category`/`score` for its category breakdown.

## traptask.yaml

```yaml
dirs:
  inputs: inputs/
  expected: expected/

cases:
- id: case_01
  description: "<one-line human summary of what this case tests>"
  tags: [<domain>, <language-or-format>, <specific-subcategory>]
# ... one entry per case

judge:
  cmd: python3 judge.py

grader:
  cmd: python3 grader.py
```

`tags` should include the same category label used as the `metrics` dict's
category field (e.g. `bug_category`), so grader.py's by-category breakdown
lines up with what's shown on the task page.

## build_cases.py -- validate, then render

```python
def validate_case(case: dict) -> None:
    """Fail loudly on authoring mistakes -- missing fields, out-of-range
    line numbers, disallowed licenses, duplicate IDs, whatever invariants
    your task needs. THE CUSTOMIZATION POINT along with render below."""
    ...

def build() -> None:
    data = json.loads(GOLD.read_text())
    for case in data["cases"]:
        validate_case(case)
        (HERE / "inputs" / case["id"]).mkdir(parents=True, exist_ok=True)
        # ... write inputs/<id>/... from case's fields (THE CUSTOMIZATION POINT)
        (HERE / "expected" / case["id"]).mkdir(parents=True, exist_ok=True)
        # ... write expected/<id>/answer.json (THE CUSTOMIZATION POINT)
```

Run `python3 build_cases.py` after every edit to `gold.cases.json` --
`inputs/`/`expected/` are generated output, never hand-edited.

Two things worth deciding here rather than later:

- **`gold.cases.json` does not have to contain answers.** A case can be a
  question kind, a seed and a size, with `build()` generating the material
  and deriving the answer from what it generated. See
  `ground-truth-sourcing.md`, "Compute the ground truth".
- **`validate_case()` is where fairness invariants live.** Anything you
  would otherwise check by reading the cases over -- no shortcut, not
  guessable, the answer absent from the inputs, enough examples to pin the
  rule down -- belongs here as an assertion, because review does not
  survive the next regeneration. The list is in `difficulty-design.md`,
  "Make fairness a build invariant".

## Case ID naming -- never let it leak the answer

A case ID like `leopard_01` or `off_by_one_case` hands the solution the
answer through the directory name alone (`inputs_dir` in `TRAP_MANIFEST` is
literally `.../inputs/<case_id>`, and a curious solution can read its own
path). Use opaque IDs (`case_01`, `case_02`, ...) and keep the real
category/label only in `expected/<id>/answer.json`, which the solution
never sees.
