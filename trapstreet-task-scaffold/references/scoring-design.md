# Scoring design -- real exploits and how they were fixed

Every item here is a real bug found by actually testing solutions against
a task, not a theoretical concern. Design the judge assuming a determined
solution author (or a skill that happens to phrase things a certain way)
will find any gap.

## Extract the answer with a sentinel, never by position

An early judge took the answer from the last non-empty line of stdout. In
one ten-case run, four correct answers scored 0.0 because the harness
printed the right figure and then wrote a short summary underneath --
several of them stating, accurately from their own point of view, that they
had complied with the format.

The reported score was 2/10. The true score was 6/10, and the task's
difficulty was nearly dialled down on the strength of that.

Ask for a sentinel line instead, and read the **last** occurrence of it:

```
ANSWER: 12345.67
```

It costs the solution one line and lets it write whatever it likes around
that. Compare numerically where the answer is a number, so `12,345.67` and
`$12345.67` are the same answer. State the convention in whatever the
solution actually reads (the task README or the per-case prompt) -- a
format rule the solution never saw is a gotcha, not a measurement. When the
sentinel is absent, score 0.0 with a reason, the same way as any other
malformed output below.

The same shape works for structured answers: ask for a fenced JSON block
with a marker and parse the last one. The principle is position
independence, not the specific `ANSWER:` string.

**The general failure this belongs to:** agentic solutions explain
themselves. Three tasks in this repo have lost correct answers to scoring
that keyed on *form* rather than content -- a code-review case that
required one of a curated list of phrasings and got a correct diagnosis at
the exact right line worded differently, an OCR case where "the first
sentence" admitted two defensible readings, and this one. A judge written
with a single terse model call in mind punishes an agent for narrating its
work, systematically and invisibly.

## Anti-shotgun

If a solution can list every plausible answer and get credit for
whichever one happens to be right, the task measures nothing. Cap how much
of the output actually counts:

- Multiple findings/guesses allowed, but only the first N are scored
  (`MAX_FINDINGS_SCORED = 5` in the reference task) -- flagging every line
  in a file, or guessing every category, doesn't help past that cap.
- State this in the prompt shown to the solution ("only your first N will
  be scored") so it's not a hidden gotcha -- a solution that doesn't know
  the rule can't be faulted for shotgunning.

## Keyword/phrase matching -- the single riskiest scoring primitive

If any part of scoring involves checking whether an explanation mentions
the right concept, two real exploits were found the hard way:

1. **Substring matching lets an unrelated sentence "hit" by accident.**
   `"none"` as a raw substring matched inside `"none of the edge cases
   apply here"` -- a sentence that explicitly disclaims relevance still
   counted as a match. Fix: word-boundary regex (`\bnone\b`), not `in`.

2. **Even word-boundary bare single words are still exploitable.** Common
   single words (`"boundary"`, `"leaking"`, `"bypass"`) show up in
   plausible-sounding but wrong explanations often enough that a solution
   can stumble into a false hit without actually having found the real
   issue. The fix that held up under adversarial testing: **remove every
   bare single-word keyword; keep only multi-word phrases** (`"off by
   one"`, not `"off"`; `"missing null check"`, not `"null"`). Multi-word
   phrases occurring together are a much stronger signal of genuine
   understanding than any single word in isolation.

3. Curate keyword lists generously with natural synonyms/inflections
   (`"off-by-one"` AND `"off by one"`; `"concurrent"` AND `"concurrently"`
   AND `"concurrency"`) -- otherwise a correct answer phrased slightly
   differently than the curator's first guess scores as a miss. This
   doesn't eliminate the ceiling below, but narrows it substantially.

**Known, accepted ceiling:** keyword-presence matching cannot distinguish
"correctly identifies X" from "mentions X while explaining it's NOT the
issue." This is a structural limit of the technique, not a bug to chase
down further -- state it plainly in the task's README rather than pretend
it's solved.

Because this style of judge scores wording, every miss it reports is also a
candidate curation gap. Read the actual output before believing a 0.0 --
`calibration.md`, "When the solution fails, suspect your data first", is
the same lesson arriving through a different door.

## Malformed-output robustness

A judge that crashes on unexpected input silently breaks scoring for that
run (often reads as "task infrastructure is broken" rather than "solution
produced garbage," which is the wrong signal). Handle, don't crash on:

- Non-JSON output, or JSON that doesn't match the expected top-level shape
  (missing key, wrong type) -- score 0.0, don't raise.
- Deeply nested/recursive JSON (can raise `RecursionError` on `json.loads`
  before you even get to your own logic) -- catch it.
- Numeric fields containing `Infinity`/`-Infinity`/`NaN` -- Python's
  `json.loads` accepts these non-standard literals by default, and
  `int(float("inf"))` raises `OverflowError` while `int(float("nan"))`
  raises `ValueError`. A solution that emits `{"line": Infinity}` must
  degrade to a clean miss, not crash the judge.
- Non-dict entries inside a list that's supposed to contain dicts (a
  solution emitting `["a string", 42, {...}]` where objects were expected)
  -- skip/ignore, don't assume every list item has the right shape.

## Deterministic (no-LLM) judges

Prefer a scoring rule you can write in plain Python over an LLM-as-judge
call, when the domain allows it -- zero grading cost, zero grading
variance, and a judge you can unit-test exhaustively (see
`tests/test_judge.py` in the reference task: 19 tests covering exact
hits, near-misses, malformed input, the exploits above, and edge cases).
Reach for an LLM judge only when the domain genuinely needs open-ended
semantic comparison that no deterministic rule can approximate.

## Partial credit vs. binary pass/fail

The reference task uses binary per-case scoring (found it or didn't) with
a run-level mean across cases -- simple, and the anti-shotgun cap makes it
hard to game. Partial credit (a ladder of milestones, each worth a
fraction of the case) is worth it when the task has a genuine, orderable
notion of "progress" (see the Minecraft `obtain_diamond` task's
wooden→stone→iron→diamond pickaxe ladder) -- don't add partial credit
just because it seems more sophisticated; only add it where "how far did
you get" is a real, orderable question for the domain.
