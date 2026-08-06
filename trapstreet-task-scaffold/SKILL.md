---
name: trapstreet-task-scaffold
description: Design and scaffold a NEW trapstreet.run task to evaluate a given agent/skill/tool -- the reverse of trapstreet-solution-scaffold (which builds a solution against an existing task). Generates the mechanical parts (traptask.yaml, judge.py/grader.py matching the TRAPTASK_MANIFEST contract, build_cases.py's validate-then-render pipeline) and guides the judgment-heavy parts through a structured interview (what does this agent/skill actually do, what counts as correct, where does ground truth come from, how is scoring made ungameable) plus a checklist of real exploits and pitfalls already found the hard way. Use whenever the user wants to build a new evaluation task, turn an agent/skill into a benchmark, design test cases for a tool, or asks things like "can we make a task out of this", "how do I evaluate my agent on trapstreet", "design a benchmark for X" -- even if they don't say "task" or "trapstreet-tasks" by name.
---

# trapstreet-task-scaffold

Scaffolds a new task directory in `trapstreet-tasks` and guides the design
decisions that make a task actually good -- discriminating, hard to game,
legally sound, and consistent with a real ground-truth pipeline.
Sister skill to `trapstreet-solution-scaffold`, which does the reverse
(build a solution against an existing task).

**Read this first, honestly:** unlike solution scaffolding, task design is
not fully mechanizable. The file layout, manifest contracts, and
aggregation logic are the same every time and the scaffold script writes
them for you. Whether the task is actually *good* -- whether it measures
something real, whether it resists gaming, whether the ground truth is
sound -- depends on understanding the specific agent/skill/domain being
tested, and that part is an interview + judgment call, not a template fill.

## Ground rules

- **Never push to the shared task repo, and never register/publish a task on trapstreet.run,
  without the user's explicit go-ahead on that specific push/publish** -- same weight as
  `trapstreet-solution-scaffold`'s submit rule. Agreeing to earlier steps (case design, scoring
  logic) is not consent to publish; ask again at that specific moment.
- **Default to local-only whenever the legal/IP question (interview step 4) is unresolved.**
  Build and test the task fully -- nothing about that requires a public remote -- but don't
  `git push` until the question is actually answered (see `references/legal-ip-checklist.md`).

## Before writing anything: interview

1. **What does the agent/skill actually do, concretely?** Not "a code
   review skill" but "given a diff, flags likely bugs with a file/line/
   description." The task's I/O contract should mirror the real thing this
   tool is used for -- don't design a task that only tests a narrow slice
   of what the tool claims to do, or one so different from its real usage
   that good performance here doesn't predict good performance there.
2. **What does "correct" mean, concretely, and who would disagree?** If
   two competent humans could reasonably disagree on whether an answer is
   right, that's a sign the scoring needs either a very carefully curated
   rubric or a different, more objective framing of the task.
3. **Where does ground truth come from?** Real historical data (leakage
   risk, but credible) or synthetic/hand-authored (no leakage risk, but
   needs real effort to feel authentic)? Read
   `references/ground-truth-sourcing.md` before deciding -- this is one of
   the highest-leverage decisions in the whole task.
4. **Does any candidate source material raise a legal/IP/liability
   question?** Read `references/legal-ip-checklist.md` and answer its
   questions explicitly before writing a single case into
   `gold.cases.json`. If the answer is unclear, default to building the
   task locally (gitignored) and resolve the question before ever pushing
   it to a public remote -- not after.
5. **How many cases, and how are they organized into categories/tags?**
   Enough to give real signal (a handful of cases barely discriminates
   anything), but every case should be worth its inclusion -- don't pad
   the count with near-duplicates of an already-covered pattern.

## Generating the mechanical scaffolding

```bash
python3 scripts/scaffold_task.py \
  --output-dir <trapstreet-tasks>/tasks/<category> \
  --task-name <task_name> \
  --case-ids case_01 case_02 case_03   # as many placeholder IDs as you'll author
```

This writes `gold.cases.json`, `build_cases.py`, `judge.py`, `grader.py`,
`traptask.yaml`, `tests/`, and `README.md`. Two things to know about what
it generates:

- **`grader.py` is written complete and usually needs no changes** -- its
  aggregation logic (mean score, pass count, by-category breakdown,
  latency, cost) has been identical across every real task in this repo.
- **`build_cases.py`'s `validate_case()` and `judge.py`'s `score_case()`
  are deliberately left as `NotImplementedError` stubs**, not empty
  functions -- running the scaffold as-is fails loudly rather than
  silently shipping a broken task. Read `references/traptask-contract.md`
  for the exact shape each function needs to fill in, and
  `references/scoring-design.md` before writing `score_case()`
  specifically -- it documents real exploits (substring-match false
  positives, bare-keyword gaming, anti-shotgun, malformed-input crashes)
  that were found by actually testing real solutions against a real task,
  not theorized in advance.

## Filling in the judgment-heavy parts

Work through the scaffold script's own printed "Next steps" in order --
each step depends on the one before it (ground-truth decisions before
case authoring, case authoring before scoring logic, scoring logic before
tests). Don't skip straight to writing `judge.py` before `gold.cases.json`
has real cases in it; the scoring design should be shaped by what the
actual cases look like, not decided in the abstract first.

**Case ID naming**: keep IDs opaque (`case_01`, not `off_by_one_case`) --
`references/traptask-contract.md` explains exactly how a descriptive ID
leaks the answer through the input directory path itself.

**Tests**: the scaffold writes one stub test per file (`test_build.py`,
`test_judge.py`) that intentionally fails until you implement the real
logic -- once you do, replace the stub test with real coverage. At
minimum: an exact-hit case, a near-miss/boundary case, and one test per
known exploit class from `scoring-design.md` that's relevant to your
scoring approach (e.g. if using keyword matching, a substring-false-
positive regression test).

**This near-miss test is also the free way to confirm the task actually discriminates.** Hand-author
a plausible-but-wrong answer -- the kind a genuine, earnest, but weak attempt would actually
produce, not a throwaway empty string -- and confirm `score_case()` scores it clearly below the
gold answer. This is a direct Python function call, no LLM involved, costs nothing, and catches
most discrimination problems (a judge too lenient to tell weak from strong) before you ever spend
money running a real solution. Do this before reaching for the optional real-run check below.

## After building: validate

```bash
python3 build_cases.py                              # regenerate from gold.cases.json
python3 -m pytest tests/ -v                          # your real tests
python3 scripts/validate_task.py <path-to-task-dir>  # structural self-consistency checks
```

`validate_task.py` catches a narrower, domain-independent class of mistake
that's easy to make and easy to miss by eye: `build_cases.py` not actually
running clean, `traptask.yaml`'s case list drifting out of sync with
`gold.cases.json` (a real copy-paste mistake), `expected/` content
accidentally leaking into `inputs/` (would hand the solution the answer),
and `judge.py` crashing instead of degrading gracefully on malformed
input. It does not replace real unit tests -- it's a second, independent
pass that catches things your own tests might not think to check.

## Optional: confirm discrimination with a real run

Unit tests verify the judge can tell right from wrong on answers *you* thought to hand-author --
they can't catch a form of wrong answer you didn't imagine. If you want stronger confidence
before publishing, run 1-2 real solutions of clearly different quality (e.g. a
deterministic/naive baseline and a genuinely competent attempt) against a small subset of cases
and confirm the scores separate meaningfully. This is optional, an extra confidence check, not a
blocking step -- the free unit-test path above is what to do first, every time.

The moment a paid model is involved this costs real money, so it follows
`trapstreet-solution-scaffold`'s cost-triage discipline exactly: no paid call before the user's
OK, prefer a free/deterministic baseline over a second paid one when a real baseline exists, and
run a handful of cases -- not the full set -- to keep the cost small while still getting a
directional signal.

## Publishing

Once the task passes its own tests and `validate_task.py`, and the
legal/IP question from step 4 of the interview is resolved: commit, and
-- after the user's explicit go-ahead (Ground rules above, no exception) --
push to the shared task repo and (if this account can) register/publish the
task on trapstreet.run so solutions can actually submit against it -- see
`trapstreet-solution-scaffold`'s `check_provenance.py` for how a
solution verifies a task is actually published before spending an API
call trying to run against it.
