---
name: trapstreet-task-scaffold
description: Design and scaffold a new trapstreet.run task to evaluate a given agent/skill/tool -- the reverse of trapstreet-solution-scaffold (a solution for an existing task). Generates the mechanical parts (traptask.yaml, judge.py/grader.py on the TRAPTASK_MANIFEST contract, build_cases.py's validate-then-render pipeline) and guides the judgment-heavy parts through a structured interview (what the tool actually does, what counts as correct, what makes it hard, where ground truth comes from, how scoring resists gaming), plus the calibration protocol that says whether the task discriminates and a checklist of exploits found the hard way. Use whenever the user wants to build a new evaluation task, turn an agent/skill into a benchmark, design test cases for a tool, fix a task that everything passes or fails, or asks things like "can we make a task out of this", "how do I evaluate my agent on trapstreet", "why is my task too easy", "design a benchmark for X" -- even if they don't say "task" or "trapstreet-tasks" by name.
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

**And the second thing to know:** intuitions about what makes a task hard
are unreliable, so the workflow below is built to find that out early and
cheaply -- probe one question before authoring a set, and never conclude
from a single run. `references/difficulty-design.md` and
`references/calibration.md` are the two files that decide whether the
finished task discriminates; the rest is craft around them.

## Ground rules

- **Never push to the shared task repo, and never register/publish a task on trapstreet.run,
  without the user's explicit go-ahead on that specific push/publish** -- same weight as
  `trapstreet-solution-scaffold`'s submit rule. Agreeing to earlier steps (case design, scoring
  logic) is not consent to publish; ask again at that specific moment.
- **Default to local-only whenever the legal/IP question (interview step 5) is unresolved.**
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
3. **What is supposed to make this hard, and is that thing real?** Answer
   in the two quantities that predict the score: **H\***, the minimum
   number of effective actions the task requires, and **s**, the layers of
   nested sub-goals and conditional branches. Performance falls off
   non-linearly in s with a sharp knee; the intuitive answers (harder
   arithmetic, defects a human would be slow to spot, capability gates a
   shell can synthesise) sit on the flat part and moved a bare harness not
   at all. Read `references/difficulty-design.md` before answering -- it
   is the difference between a task that discriminates and one everyone
   passes.
4. **Where does ground truth come from?** Computed from a seed (no answer
   for anyone to get wrong, and leakage is impossible by construction),
   real historical data (leakage risk, but credible), or hand-authored
   (no leakage risk, but needs real effort to feel authentic)? Read
   `references/ground-truth-sourcing.md` before deciding -- this is one of
   the highest-leverage decisions in the whole task, and the computed
   option is under-used.
5. **Does any candidate source material raise a legal/IP/liability
   question?** Read `references/legal-ip-checklist.md` and answer its
   questions explicitly before writing a single case into
   `gold.cases.json`. If the answer is unclear, default to building the
   task locally (gitignored) and resolve the question before ever pushing
   it to a public remote -- not after.
6. **How many cases, and how are they organized into categories/tags?**
   Enough to give real signal (a handful of cases barely discriminates
   anything), but every case should be worth its inclusion -- don't pad
   the count with near-duplicates of an already-covered pattern. Plan on
   sourcing roughly **three times** what you intend to ship: SWE-bench
   Verified discarded 68.3% of naturally sourced candidates under review,
   and the probe below will discard some of yours.

## Probe one candidate question before authoring the set

The order of the next two steps is the point, so don't collapse them.
Take **one** candidate question and confirm both halves:

- the configuration you intend to pass, passes; and
- a bare configuration, given every resource it can reach, **fails**.

This is GPQA's two-sided filter, and it is cheap precisely because it is
one question. Run it after the interview and before writing a set around
the idea. The `core_pdf_ocr` capability gate in
`references/difficulty-design.md` died at exactly this step -- the harness
wrote its own OCR against `Vision.framework` and read every page -- and it
died before any cases had been authored around it, which is the only
reason that discovery was cheap.

If the bare configuration passes, the question is not measuring what you
think. Change the design and probe again before scaling up -- and reach
for horizon rather than for a harder question. Because the falloff has a
knee, the score is a dial you set rather than a property you discover:
pick the score the reference configuration should get, then rescale the
horizon until it gets it.

`references/calibration.md` covers this and everything downstream of it.

## Generating the mechanical scaffolding

```bash
python3 scripts/scaffold_task.py \
  --output-dir <trapstreet-tasks>/tasks/<category> \
  --task-name <task_name> \
  --case-ids case_01 case_02 case_03   # as many placeholder IDs as you'll author
```

This writes `gold.cases.json`, `build_cases.py`, `judge.py`, `grader.py`,
`traptask.yaml`, `tests/`, and `README.md`. What's stubbed and what isn't:

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
- **`judge.py` ships a working `extract_sentinel_answer()` /
  `answers_match()` pair for scalar-answer tasks** -- use them rather than
  reading a position in stdout (`scoring-design.md` explains the ten-case
  run where four correct answers scored 0.0 because the solution wrote a
  summary under its answer). Delete them if your task's answer is a list of
  findings rather than a single value.
- **`build_cases.py` ships a working `assert_answer_absent_from_inputs()`**
  and calls it per case. It is the one fairness invariant that is fully
  mechanical; the rest are task-specific and go in `validate_case()` (see
  `references/difficulty-design.md`, "Make fairness a build invariant").

## Filling in the judgment-heavy parts

Work through the scaffold script's own printed "Next steps" in order --
each step depends on the one before it (difficulty and ground-truth
decisions before the probe, the probe before case authoring, case
authoring before scoring logic, scoring logic before tests). Don't skip
straight to writing `judge.py` before `gold.cases.json` has real cases in
it; the scoring design should be shaped by what the actual cases look
like, not decided in the abstract first.

**Case ID naming**: keep IDs opaque (`case_01`, not `off_by_one_case`) --
`references/traptask-contract.md` explains exactly how a descriptive ID
leaks the answer through the input directory path itself, and
`validate_task.py` enforces it (IDs may differ only by a numeric suffix).

**Tests**: the scaffold writes one tripwire test per file
(`test_build.py`, `test_judge.py`). Each passes only while its function is
still the stub and goes red the moment you implement it -- that red is the
cue to delete it and write real coverage. At minimum: an exact-hit case, a
near-miss/boundary case, and one test per known exploit class from
`scoring-design.md` that's relevant to your scoring approach (e.g. if
using keyword matching, a substring-false-positive regression test).

**Two free checks, both pure Python, both worth running before any model is involved:**

1. **The near-miss test tells you the judge discriminates.** Hand-author a
   plausible-but-wrong answer -- the kind a genuine, earnest, but weak attempt would actually
   produce, not a throwaway empty string -- and confirm `score_case()` scores it clearly below
   the gold answer. This catches a judge too lenient to tell weak from strong.
2. **The ablation replay tells you each planted mechanism discriminates.** For every trap, decoy
   or gap in the task, regenerate the answer *with that mistake made* and compare against the
   truth. If the answer barely moves, the mechanism is decoration -- the task can't detect that
   mistake, it only rewards not making it. Compare **item by item, never by total**; your
   domain's conservation identity will hide errors from a total (`references/calibration.md`).

## After building: validate

```bash
python3 build_cases.py                              # regenerate from gold.cases.json
python3 -m pytest tests/ -v                          # your real tests
python3 scripts/validate_task.py <path-to-task-dir>  # structural self-consistency checks
```

`validate_task.py` catches a narrower, domain-independent class of mistake
that's easy to make and easy to miss by eye: `build_cases.py` not actually
running clean, `traptask.yaml`'s case list drifting out of sync with
`gold.cases.json` (a real copy-paste mistake), a case ID that describes
its own case, `expected/` content accidentally leaking into `inputs/`
(would hand the solution the answer), and `judge.py` crashing instead of
degrading gracefully on malformed input. It does not replace real unit tests -- it's a second, independent
pass that catches things your own tests might not think to check.

## Calibrating with real runs

Unit tests verify the judge can tell right from wrong on answers *you* thought to hand-author --
they can't catch a form of wrong answer you didn't imagine. Running 1-2 real solutions of clearly
different quality (a deterministic/naive baseline and a genuinely competent attempt) against a
small subset of cases is how you find those. The free checks above come first, every time; this
is what you do once they pass.

**The discipline that matters here is not "run it" -- it's "don't conclude from one run."** Eight
rounds of design changes on a real task each produced a conclusion, and a repeat run showed all
eight had been reading the same ±1 spread. `references/calibration.md` has the numbers. So:

- Run the same build **at least 3 times** before any score changes your mind about anything.
- Report **per-question success rates**, not a total -- a total hides four questions at 100% and
  one at 0%.
- If a decision hinges on ±1 question, you need more trials, not more design.
- **Read the transcript before recording a failure.** Six apparent solution failures in one day
  were authoring bugs. A failing case is evidence about the task at least as often as about the
  solution.

The moment a paid model is involved this costs real money, so it follows
`trapstreet-solution-scaffold`'s cost-triage discipline exactly: no paid call before the user's
OK, prefer a free/deterministic baseline over a second paid one when a real baseline exists, and
keep the case subset small. Repeating a 3-case subset three times is a better spend than one pass
over 10 cases, because the first produces a number you can act on and the second doesn't.

## Publishing

**Check the clock before you check anything else.** Latency gates whether a
task works as a public board at all -- one otherwise-good build averaged 27
minutes per case and was unpublishable regardless of question quality. Look
at the mean *and* the tail; a wide spread is signal worth keeping, a slow
mean is a rebuild.

**If cases run anywhere near 600s, the README has to say so.** That's the
default per-case ceiling in the *solution's* `trap.yaml`, and nothing in
`traptask.yaml` can raise it. Past it the case is killed at exit 124 and
scores 0.0, which reads as a wrong answer rather than a misconfiguration.
Ship a copy-pasteable `trap.yaml` snippet with the `timeout:` this task
needs. `references/calibration.md` has the three ceilings and who owns
each, plus the cost caveat to note in the README (cached runs are
mispriced, and that is not something `grader.py` can fix).

Once the task passes its own tests and `validate_task.py`, the latency
check above is clear, and the legal/IP question from step 5 of the
interview is resolved: commit, and
-- after the user's explicit go-ahead (Ground rules above, no exception) --
push to the shared task repo and (if this account can) register/publish the
task on trapstreet.run so solutions can actually submit against it -- see
`trapstreet-solution-scaffold`'s `check_provenance.py` for how a
solution verifies a task is actually published before spending an API
call trying to run against it.
