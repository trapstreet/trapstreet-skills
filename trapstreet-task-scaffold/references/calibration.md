# Calibration -- finding out whether the task measures anything

Design decisions in `difficulty-design.md` are hypotheses. This file is how
you find out whether they were right, in the order the checks pay off:
before the case set exists, while it is being built, and before it is
published.

## Probe one question before authoring the set

GPQA keeps a question only if domain experts get it right **and** skilled
non-experts with unrestricted web access and half an hour get it wrong.
Both halves.

Translated: the configuration you intend to pass must pass, **and a bare
configuration given every resource must fail**. Run both on *one* candidate
question before writing a set around it. One question is cheap enough that
this is not a step worth skipping; ten questions is not, which is exactly
why it has to happen first.

The `core_pdf_ocr` result in `difficulty-design.md` is the second half
working -- the question was discarded before any cases had been written
around it. Had the probe come after authoring, the whole set would have
gone with it.

When planning the case count: SWE-bench Verified discarded **68.3%** of
naturally sourced candidates under human review. Prepare roughly three
times what you intend to ship.

## A single run is noise

Eight rounds of design changes on `ledger_audit` produced 8, 8, 10, 9, 8,
9, 10 out of 10. Each round the ±1 was read as evidence about the change
that had just been made, and a conclusion was written about it.

Then the same three questions were run three times each, unchanged:
`1,1,1`, `0,1,1`, `0,1,1`. Per-question success on the hard tier was about
2/3, which makes the expected total 8.3 with a spread that covers 7 to 10
comfortably. **The design changes had produced no measurable effect and
every one of those conclusions was reading noise.**

So the rule is not "always run the full set" -- it is that a score you draw
a conclusion from needs to survive repetition:

- Before concluding anything from a score, run the same build **at least 3
  times**.
- Report **per-question success rates**, not a total. A total hides that
  four questions sit at 100% and one at 0%.
- If a decision hinges on ±1 question, the answer is more trials, not more
  design.

τ-bench's `pass^k` is the formal version: a system at 90% pass@1 sits at
57% when all 8 attempts must succeed.

## Prove each mechanism changes the answer -- item by item

Every trap, decoy and gap should be replayed *with the mistake made*, and
the result compared against the truth. If the difference is small, the
mechanism is decoration: the task cannot detect that mistake, it only
rewards not making it.

Compare **per item, never by total**. In a receivables ledger, total open
equals debits minus credits plus unapplied, so any error that merely moves
money between invoices leaves the total untouched. Written against totals
first, every one of these checks reported "no effect" for mechanisms that
in fact changed a third of the allocation.

Whatever your domain's conservation identity is, it will hide errors from a
total-based check. Find it before you trust one.

This is a pure-Python replay with no model in the loop -- same cost profile
as the near-miss judge test, and worth running at the same time.

## When the solution fails, suspect your data first

Six times in one day a failure turned out to be the task's fault:

| what the harness did | what our data said |
|---|---|
| excluded a row dated `2026-02-30` | our date arithmetic assumed 30-day months |
| answered as at the period end the header declared | our entries ran past that date |
| carried unapplied cash forward to later invoices | our rule parked it forever, and never demonstrated which |
| diagnosed the bug at the exact right line | its wording was not in our keyword list |
| read "the first sentence" as the quoted speech | our gold included the following clause |
| printed the right figure, then a summary | our judge read the last line |

In every case the harness's reading was defensible and ours was the one
that needed fixing. **A failing case is evidence about the task at least as
often as it is evidence about the solution.** Read the transcript before
recording the score.

## Cost and latency are part of the result

Watch the clock as well as the score. On one build the easy questions took
9-24 seconds and the hard ones 137-3871 -- a 10-40x spread that separates
solutions even where accuracy does not. That same build averaged 27 minutes
per case, which made it unusable as a public board regardless of how good
the questions were. Check the mean and the tail before publishing, not
after.

### The timeout is the solution's, and its default will bite you

`trap` has three wall-clock ceilings and the task author owns only two of
them:

| ceiling | default | owned by |
|---|---|---|
| solution, per case | **600s** | the *solution* author, in `trap.yaml` |
| `judge.timeout`, per case | 300s | the task author, in `traptask.yaml` |
| `grader.timeout`, per run | 120s | the task author, in `traptask.yaml` |

There is no task-side field that caps or raises how long a solution may
run. So a slow task silently punishes every solution that never thought
about it: past 600s the process is killed, the case is recorded as exit
124, and a judge that only checks `exit_code != 0` scores it 0.0 with a
generic reason. On the board that reads as a wrong answer, not a
misconfiguration.

The `ledger_close` build that ships averages 509s per case against that
600s default, with individual hard cases well past it. Two things follow:

- **State the required `timeout:` in the task README**, in a copy-pasteable
  `trap.yaml` snippet, the way `personality/mbti_profile` does. It is the
  only channel a task author has.
- **Make the judge say "timed out" explicitly.** Branch on exit code 124
  and return a reason that names the ceiling, so the run is diagnosable
  from the metrics alone. The scaffold's `judge.py` does this; the
  `grader.py` it generates also counts `n_timed_out` at run level, because
  one timed-out case is a solution problem and ten is a task problem.

And note that a task whose honest runtime exceeds the default by a lot is
telling you something -- see the 27-minute build above.

**Caching distorts the cost number, and not in the task's control.** One
harness served 98.9% of a turn's prompt tokens from cache (`cacheReadTokens
43,136` against `inputTokens 481`). `trap`'s cost model has two dimensions,
prompt and completion, with no cache tier, so a cached run is mispriced by
roughly two orders of magnitude. This is not vendor-specific -- Anthropic
and OpenAI price cached input separately too.

Nothing in `grader.py` can fix this; it reads the cost the runner reports.
The fix is a third price dimension and a parser that reads the cache field,
upstream in `trap`. Until then, treat cost comparisons between a
stable-prefix solution and a cache-missing one as unreliable, and say so in
the task README rather than let the board imply a precision it does not
have.

And do not design to defeat caching. A solution that keeps a stable prefix
genuinely is cheaper to run, and that is worth measuring.
