# Difficulty design -- what actually makes a task hard

Read this before authoring the case set, not after. Everything here cost a
calibration round on a real task (`ledger_audit`, `ledger_close`,
`core_pdf_ocr`) and most of it is counter-intuitive enough that it will be
re-learned the expensive way otherwise.

## Difficulty lives in horizon and depth, not in per-step hardness

`ledger_audit` was single-shot: one prompt, one fully-visible sheet, one
answer. Eight rounds of making the *step* harder -- multi-rule settlement,
an induced rather than stated policy, a mid-period policy change,
out-of-order records, aggregates with every closed-form shortcut blocked,
larger and messier data -- moved a bare harness by 0 to 2 questions out of
10, with no trend.

Restructuring the *same domain and the same questions* into a year of
monthly files with a policy memo, a customer master, a document index, a
decoy and one short month took the same harness from 9-10 out of 10 to 1
out of 10.

The published work says why, and it names the two things worth measuring:

- **Intrinsic horizon (H\*)** -- the minimum number of effective actions
  needed to complete the task. Not how many an agent takes; the floor.
- **Compositional depth (s)** -- how many layers of nested sub-goals and
  conditional branches sit between the question and the answer.

Performance degrades non-linearly in **s**, with a sharp knee: success
"transitions abruptly from partial robustness to near-systematic failure."
Planning failures dominate, because they arise early and propagate through
everything downstream. Single-step computational difficulty is the flat
part of that curve, which is why eight rounds of making the step harder did
nothing.

Both are countable before you build anything. `ledger_audit` was H\* ~ 1
and s ~ 1 -- read one sheet, compute. `ledger_close` at 12 months is H\*
in the dozens (open the memo, resolve the policy, open each month, filter,
reconcile) and s of 3-4, because the memo's rule change gates how each
month is read, which gates the aggregate. That difference, not the
arithmetic, is the entire 9/10 -> 1/10.

**Make H\* and s build parameters**, so difficulty is something you rescale
rather than redesign. `ledger_close` exposes number of periods, items per
period, supplement size, decoy count, and how much evidence the memo gives
for the rule change. Two builds and a rescale walked the score 9 -> 1 -> 6;
eight rounds of redesign had not moved it at all.

Two practical consequences of the knee:

- **When a build lands at the ceiling or the floor, reach for the
  parameters** -- you are on a flat part of the curve, and inventing new
  question types is the expensive move that does nothing. A build at 1/10
  is not "hard", it is past the cliff and measuring nothing, exactly like a
  build at 10/10.
- **Aim the case set at the knee, and record where each case sits.** Carry
  s in `expected/<id>/answer.json`, echo it from `judge.py` into the
  metrics dict, and point `grader.py`'s `CATEGORY_FIELD` at it. The
  by-category breakdown is then the curve itself: one run tells you which
  depth the configuration you are measuring falls off at, instead of an
  aggregate that hides it. Same reason `calibration.md` asks for
  per-question rates rather than a total.

## Horizon is the calibration knob

Take the knee seriously and it inverts the whole workflow. If the falloff
is that sharp, **the score is not something you discover about a task, it
is something you set.** Push the horizon past the knee and any target
score lands. That is the calibration knob eight rounds of arithmetic
redesign were looking for and never found.

So don't build a task and then ask what it scores. Pick the score the
reference configuration should get, and rescale until it gets it -- two
builds and a rescale, against eight rounds that moved nothing.

**Two axes, not one.** AgentCE-Bench names the pair, and keeping them as
separate parameters is what makes the knob usable:

- **Scalable horizons** -- how many hidden slots must be found and chained
  before the answer exists. This grows H\* directly.
- **Controllable difficulty** -- the decoy budget: how much material is
  present that has to be recognised and rejected. This raises difficulty
  *without* lengthening the minimum path.

They cost different things, which is the practical reason not to conflate
them into one "difficulty" number. Horizon buys difficulty with wall-clock,
and wall-clock is a publishing gate -- it is what put one build at 27
minutes per case and made it unpublishable regardless of question quality
(`calibration.md`). Decoys buy difficulty without extending the minimum
path, so when the latency gate binds, the decoy budget is the axis with
room left in it.

**Where to aim:** not the ceiling, not the floor, but the region where
per-question success sits well away from 0 and 1. That is also the region
of highest variance -- the knee is precisely where a single run tells you
least, so the "at least 3 trials" rule in `calibration.md` bites hardest
exactly where you will be doing the most calibrating.

**And say where you set it.** Because the score is a dial, "this
configuration scores 6/10" means nothing without the build parameters next
to it. Put the parameter values and the measured score in the task README
as a table, the way `ledger_close` does -- otherwise the next person
regenerates at different settings and compares two numbers that were never
comparable.

## Do not hand the procedure over in the question

The single most repeated mistake -- seven of the first ten questions.

> "The Balance column should roll forward line by line: each balance is the
> one above it plus the Debit and minus the Credit on that line. Exactly one
> line breaks that rule. Identify its Voucher number."

That is a specification. The solution writes six lines of Python and
returns the answer. Compare:

> "How much did this account bill Cedarworks Ltd over the period?"

**Test:** if the question reads like a spec a junior could implement
without understanding the domain, it hands over the procedure.

The fix is to ask in the language a practitioner would actually use, and
move the vocabulary into a glossary inside the material itself. It is free
difficulty, and it is what the task claimed to be asking in the first
place.

## "Hard for a human to spot" is not "hard for an agent"

Three defects were planted that a human auditor would be slow to find: a
broken balance roll, a duplicated posting, a debit/credit reversal. A bare
harness scored 5 out of 5 on them, because each has a mechanical signature
and the agent has a shell.

The two properties are unrelated. Anything a six-line script finds is a
floor, not a ceiling.

## A capability gate the shell can synthesise is not a gate

`core_pdf_ocr` ships scanned pages with no text layer, to a text-only
model. That looked like a guaranteed floor. The harness ran `pdftoppm`,
found no OCR binary, discovered it was on macOS, wrote an Objective-C
program against `Vision.framework`, ran it twice to cross-check, and
transcribed all four pages correctly.

Two separate lessons, and the second is the more dangerous one:

- **Test any proposed gate:** is it about *information that is not on the
  machine* -- the contents of an earlier session, something that happened
  after the training cutoff -- or about a capability that merely is not
  wired up? Only the first is a gate. Anything a shell plus a compiler can
  reach will eventually be reached.
- **A gate that depends on what is installed is a validity problem, not
  just an accessibility one.** The same task on a Linux runner with no
  tesseract fails for reasons that have nothing to do with the solution.
  Scores that vary with the environment are noise once they are pooled
  across users -- which is exactly what a public board does.

## Make fairness a build invariant, not a review step

Review does not scale and does not survive the next regeneration. An
assertion does. Put these in `build_cases.py`'s `validate_case()` and let
the build refuse to emit a case that violates one.

- **The rule can be induced.** Whatever the solver must infer, the worked
  examples must pin down. Count the examples that *discriminate* the
  intended rule from the plausible simpler one -- not the examples that
  merely exist. Two of three "behaviours" in one build turned out to be
  observationally identical, so an invariant demanding all three was
  satisfied by evidence that taught nothing.
- **One example is not evidence of a rule.** A harness saw its induced
  policy match 14 of 15 worked rows and read the odd one as a keying error
  -- on one example, that is the better reading. Require three.
- **Nothing unexplained after the examples stop.** Every phenomenon in the
  region the solver must work out must have appeared in the region that was
  worked through, or a defensible reading meets a situation the examples
  never covered and is marked wrong for guessing differently.
- **No shortcut.** Check the answer against every closed form the data
  affords. One build's hardest question turned out to equal closing balance
  minus opening balance -- the easiest question wearing a hat, and it was
  passing while the genuinely hard ones failed.
- **Not guessable.** An answer drawn from a small set measures nothing. One
  case asked "how many distinct regions", an integer in 1..4; a blind guess
  scored ~25%.
- **The answer does not appear in the inputs**, including any README the
  solution can read. Assert it. Case IDs must be opaque for the same reason
  -- a solution can read its own `inputs_dir` path (see
  `traptask-contract.md`, Case ID naming).

Whether each planted mechanism actually *does* anything is a separate
question, and a measurable one: see `calibration.md`, "Prove each mechanism
changes the answer".

## A third axis: what the material contains

Horizon and depth are properties of the *procedure*. There is a third axis
that neither of them touches, and `pdf_chart_reading` cost three probe rounds
and $6.29 to find it.

The predecessor task shipped a PDF whose second half had no text layer. Its
best pipeline scored 20/20 and would not come down:

| Probe round | What was made harder | Result |
|---|---|---|
| 1 | Counting, medians, ranking, cross-page, two kinds of unanswerable | 18/18 correct |
| 2 | Eight releases, 89 pages, near-identical weeks | 8/8 correct |
| 3 | **Rasterised charts -- the value only exists as geometry** | **3/12** |

Rounds 1 and 2 raised depth and horizon. Neither moved anything. Round 3
changed neither, and broke the ceiling on the first attempt.

The premise of the old task was the diagnosis: "half the pages have no text
layer" is a property of the **file**, not of the **content**. Every figure it
asked for was still printed as a numeral somewhere on the page, so any
pipeline that reached the pixels read it off. The successor asks for values
that were never written down anywhere -- a bar's height against a gridline,
the number of dots in a row.

> **Ask for a number that was never written down.** "The text layer is
> missing" describes the file. "The number was never written down" describes
> the document, and only the second survives a model that can see.

### Picking the document is a difficulty decision

RealDocBench evaluates nine parsing systems across four regulated domains and
finds difficulty concentrated, not spread: clean mortgage forms are "nearly
saturated" (top systems 92-98% per-field, within ~5 points of each other),
while medical is the hardest domain outright (best 89.8%, weakest 46.9%) --
driven by handwriting and checkbox grids -- and finance is the most
discriminative (92.7% vs 82.9% among strong systems). On *clean, undegraded*
charts, frontier models sit at 70-88% before you do anything at all.

Ranked by what they cost a frontier model, not a weak parser:

1. **Is any answer un-printed?** Charts, plots, maps, schematics -- values
   that exist only as geometry.
2. **Is any of it handwritten?** The hardest RealDocBench domain is hardest
   for this.
3. **Does it need a domain convention to read correctly?** Face value vs cash
   value, average-of-daily vs Wednesday, unit scale.
4. **Are there structurally absent fields** -- blanks that must be reported
   empty, a figure the release simply does not break down that way?
5. **Is it long *and* image-only?** Worth ~30 points past ~100 pages, and it
   competes with the context window.
6. **Is the capture degraded?** Real, but it separates parsers from each
   other rather than the top model from the field: photographic distortion
   costs specialised parsers 25% and one frontier model 3.4 points.

The anti-pattern, which is what the predecessor was: a clean, digital-born,
fully-printed statistical table. Saturated by construction, and no amount of
question design moves it.

## If the answer was generated by a deterministic encoding, it can be inverted

Un-printed values buy difficulty against a *perceiver*. They buy nothing
against a *measurer*, and this is worth knowing before promising anyone that
a task cannot be aced.

A bar chart is not a lossy picture of a number, it is a lossless linear
encoding of one: count n was rendered as height n x unit. Measuring the
height and dividing recovers n exactly. On `pdf_chart_reading` the arms
ranked:

| Pipeline | Score | Cost |
|---|---|---|
| Measure the pixels, model reads the resulting table | **0.864** | $0.10 |
| Vision model, stronger model, whole page at 150 dpi | 0.727 | $5.20 |
| Vision model, same pipeline, cheaper model | 0.591 | $1.93 |
| Vision model, PDF handed over natively | 0.273 | $0.11 |
| Text extraction / OCR | 0.000 | $0.23-0.37 |

The measuring pipeline beat the best vision pipeline by 14 points at one
fiftieth the cost, and its three failures were measurement bugs rather than
reasoning ones. A stronger model helps the perceivers -- bar-height reading
went from 0.5-0.7 to 0.9 -- and still loses to a ruler.

So: if the requirement is "nothing should reach 100%", un-printed is not
enough. The answers have to need **semantics that measurement cannot supply**
-- a footnote that changes what a figure means, a conflict between what a
table prints and what a figure shows, a quantity the document declines to
break down. One case of that kind (`case_21`: table 1 prints the longer-run
value as 2.0, figure 3.C puts everyone in the bin labelled 1.9-2.0, and the
question asks which *range*) is what a measuring script cannot fake.
