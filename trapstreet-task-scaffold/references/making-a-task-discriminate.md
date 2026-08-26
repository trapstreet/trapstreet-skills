# Making a task discriminate -- why four designs failed and one worked

A task that every solution passes, or that every solution fails, measures
nothing. This file is about the part that is easy to get wrong: choosing a
*difficulty axis* along which the tools you care about actually differ.

Everything here comes from building a PDF-parser benchmark. Four case sets
failed to separate the tools before one succeeded, and the failures were all
the same failure wearing different clothes.

## The rule: disorder is recoverable, absence is not

A capable model repairs a garbled input. Hand it a table whose rows have been
flattened into the wrong order and it reconstructs the answer from context,
headers and plausibility. Whatever the tool mangled, the model un-mangles, and
the difference between two tools washes out of the score.

What the model cannot do is invent content that never arrived.

So a task discriminates when its cases depend on information that is
**destroyed** for some solutions, not merely **disarranged**. Concretely, for
document tasks:

| axis | discriminates? | why |
|---|---|---|
| structure is garbled but present | no | the model rebuilds it |
| reading order is wrong | no | the model reorders |
| content exists only as pixels | **yes** | a text-only path receives nothing |
| the encoding is not invertible | **yes** | same |
| the file will not open at all | **yes** | same |

Measured, on the same document and the same model: four case sets asking how
*well* structure survived produced scores of 17-20/20 across four pipelines --
inside the noise. One case set asking whether the content *arrived* produced
0.35 to 0.90.

The general form: **ask what a failing solution physically does not have.**

## Trust only end-to-end runs. Every proxy lies.

The temptation is to grade the intermediate artefact -- how much of the text
survived, how many table cells kept their labels -- because it is cheap and it
feels like it measures the tool rather than the model. Three such proxies were
built for the PDF task. All three failed, and two failed in opposite
directions:

| proxy | what it predicted | what the runs showed |
|---|---|---|
| value within ~220 chars of its row label | 10 of 11 cells recoverable | a whole 19-column row fits in that window; it cannot see columns at all |
| value at the right ordinal position in the row | no parser can locate 4 of the cells | one parser answered all four -- its output has real headers, so the model reads those instead of counting |
| overall association-preservation % | the OCR pipeline worst, at 31% | that pipeline scored highest, 20/20 |

Intermediate quality and answer quality are different variables. Budget for
real runs; do not design a case set around a number you have not validated
against outcomes.

## Verify the failure is present before authoring a single case

If the task is meant to expose a specific weakness, reproduce that weakness
first, on the documents or inputs you actually have. This costs minutes and
saves a full authoring pass.

Two candidate corpora were rejected in under ten minutes each this way, and one
reported failure mode -- a parser emitting two-column pages in raster order --
**did not reproduce at all** on seven real two-column papers. Both apparent
hits turned out to be bugs in the detection script rather than in the parser:
one was a vertical margin stamp whose y-coordinate says nothing about reading
order, the other a full-width table split at the page midline and its right
half read as an intruding column.

Had the cases been authored first, they would have been testing something that
does not happen.

## Cases sourced from a bug tracker still need reproducing

Sourcing difficulty from the tool's own issue tracker is a good instinct -- it
grounds case selection in something real instead of your imagination. But the
person who filed the issue had a file that triggers it. You may not.

Of four reported failure modes examined, one could not be reproduced, one was
already covered by an existing task, one needed a document carrying a specific
defect that could not be sourced, and one was testable. Check each against
"does this produce a wrong *answer* to a question about the content?" before
building on it.

## Toy questions do not discriminate; realistic ones do

A first case set asked "what value sits at row X, column Y?" Every solution
that could read the page scored full marks -- the task carried exactly one bit
of information per solution.

Questions of the kind the domain's practitioners actually ask discriminate for
two independent reasons:

1. **They need several pieces right at once.** If a tool delivers 90% of the
   inputs correctly, a single-input question fails 10% of the time and a
   five-input question fails 41% of the time. Compound questions amplify small
   differences into visible ones.
2. **Their answers are usually not printed anywhere in the source** -- a ratio,
   a difference, a base reconstructed by undoing a change column. That also
   makes them robust against a solution that simply echoes its input.

They name no cell, often no table. Working out *which* figures matter and
*what* to do with them is the task.

## A discriminating task is not the same as a ranking

Watch what shape the results take. A benchmark where everything that passes
scores 100% has one bit of resolution: capability gate, not quality gradient.
That may be exactly what you want -- "does this pipeline handle scanned pages,
yes or no" is a real question -- but decide it deliberately and say so in the
README, rather than discovering it after publishing.

If you want a gradient *within* the group that passes the gate, the cases have
to be hard for reasons beyond the gate itself. Compound reasoning questions are
the cheapest way to get one.

---

# Controls and confounds — five lessons from a capability-stacking task

All five came out of one task in one day, each after a measurement contradicted
what the design assumed. They are ordered by how much they cost to find.

## 1. Both sides of the match can telegraph, and fixing one moves the giveaway

The obvious defect is a request that states its own disqualifying constraint
("the original has to stay exactly where it is"). Five of six scenarios did, and
that alone makes a case a sentence-match rather than a discrimination.

But fixing only the request accomplishes little, because there are three
surfaces and a model will use whichever is easiest:

| surface | the giveaway | what it looks like |
|---|---|---|
| the request | states the constraint | "it must not go out yet" |
| the **competitor** description | confesses its own limitation | "not for holding a message back pending review" |
| the **correct** tool's description | advertises the matching virtue | "Use when the sender wants to review before anything leaves the mailbox" |

Real tool documentation **sells**. It advertises what a tool is for and does not
volunteer why you should not pick it. A competitor that confesses is not a
competitor, it is an answer key. Strip usage guidance from the correct tool too,
or the model simply matches on that instead.

Once nothing is stated outright, the audit field has to change meaning with it:
record **the inference a reader must make**, not the sentence that gives it away,
or "hard but fair" becomes unverifiable.

## 2. A failed difficulty band means change the instrument, not add cases

The band failed — a strong model scored 15/15 including the hardest cell. The
tempting response is more scenarios. The correct response was to ask what the
design had *excluded*, and the answer was substantial: every competitor was
strictly wrong on its semantics, and skills were schemas rather than
instruction-bearing cards. Both exclusions were deliberate, both were defensible
for gradeability, and together they defined out of existence the mechanism that
actually carried the phenomenon.

Adding the excluded mechanisms took one afternoon and the band then separated on
every scenario. Nine more scenarios in the original voice would have bought nine
more perfect scores.

**Ask what your invariants forbid, not just what your cases cover.** An
invariant that makes a task gradeable can also make it blind.

## 3. Near-determinism means a stable wobble is a design fault, not noise

A curve came out non-monotone. The natural reading is sampling noise and the
natural fix is repeats. Three passes per cell returned **19 of 21 cells
identical**, every median reproducing the single pass exactly.

So the wobble was a stable property of those cells and no amount of sampling
would have removed it. Two consequences:

- **One pass per cell is enough** on an instrument like this, which frees the
  budget for more cases instead of more repeats.
- **A reproducible oddity is a lead, not noise.** Go looking for a confound.

## 4. A control can hold on one axis and be absent on the orthogonal one

Position was carefully controlled **between the two arms being compared** — same
seed, same permutation, base skills at identical indices — and asserted in tests.
It was completely uncontrolled **across the levels of the dose ladder**, which is
the axis the dose-response curve is read along. The same skill sat at index 9,
then 1, then 14.

The bug underneath: the composer shuffled the *assembled* list, and a shuffle's
permutation depends on the list's **length**, so adding skills reordered
everything already present.

Fix: order by a stable per-item sort key rather than shuffling the assembled
list, so adding items only interleaves and never rearranges. Where two arms must
also match, key the added items off their **slot** (pack index, position in pack)
rather than their name — different names would otherwise interleave differently.

Then assert both properties, because they are genuinely different claims:

```
base items at identical absolute indices in both arms      (protects the arm comparison)
base items in the same relative order at every level       (protects the dose curve)
```

Re-measuring after the fix changed real outcomes — one cell went 0.50 (stable
across three passes) to 1.00, and the only semantic-confusion failure ever
observed disappeared, having been a position artifact. **Ordering moved results
about as much as composition did.**

## 5. Eliminate explanations by measurement, and the last one standing earns the spend

The curve stayed non-monotone after the position fix. By then two explanations
had been ruled out by measurement rather than argument — sampling noise (repeats)
and position (the fix) — which left the plainest one: three scenarios is too
coarse. Each cell was near-binary, so one scenario flipping moved a level mean by
a tenth.

That is not a disappointment, it is a justified budget. Authoring more cases is
the expensive step, and it should be reached by elimination, not started with.
Cheap measurements first — repeats, a probe, a closed-book check — each one
either finds the fault or removes a suspect.
