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

The published work says why: agent performance degrades non-linearly in the
number of nested sub-goals, with a sharp knee, and planning failures
dominate because they arise early and propagate. Single-step computational
difficulty is the flat part of that curve.

**Make horizon and depth build parameters**, so difficulty is something you
rescale rather than redesign. `ledger_close` exposes number of periods,
items per period, supplement size, decoy count, and how much evidence the
memo gives for the rule change. Two builds and a rescale walked the score
9 -> 1 -> 6; eight rounds of redesign had not moved it at all.

Practical consequence: when a first build lands at the ceiling or the
floor, reach for those parameters. Inventing new question types is the
expensive move that usually does nothing.

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
