# Ground truth sourcing -- real vs. synthetic, and the leakage tradeoff

## The core tension

**Real data** (an actual historical bug, an actual document, an actual
past event) is more credible and harder to dismiss as artificial, but
risks having been seen during a model's training -- if so, the model can
"answer" from memorized association rather than genuinely reasoning about
the case in front of it, and the task stops discriminating good solutions
from lucky ones.

**Synthetic/original data** (a hand-authored puzzle, an injected bug) has
zero leakage risk by construction, but needs the author to do real work to
make it feel authentic and needs its own credibility case (why should
performance here predict performance on the real thing?).

Neither is categorically better -- pick per-task based on what's available
and what the domain needs. Some real tasks in this repo mix both: original
content where leakage risk is unacceptable (word puzzles), real content
where leakage risk is mitigable (obscure bugfix commits, real API docs).

If you land on the synthetic side, read the next section before writing a
single answer down -- *how* the synthetic answer is produced matters as
much as the real/synthetic choice itself.

## Compute the ground truth. Never author it.

`gold.cases.json` in both ledger tasks carries a question kind, a seed and
a size -- and no answers. `build_cases.py` generates the data from the
seed and derives the answer from the data it just generated.

Three things follow, and the third matters more than it sounds:

- Authoring cost per case drops to three lines of JSON, so scaling the set
  up or regenerating it at a different difficulty is nearly free (see
  `difficulty-design.md` on making horizon and depth build parameters).
- There is no corpus to be contaminated by -- leakage is structurally
  impossible, not merely improbable.
- **There is no answer for a human to get wrong.** A hand-authored answer
  is one more thing that can be subtly inconsistent with the material, and
  when a solution then "fails" that case, the failure looks like the
  solution's. Six such failures in one day turned out to be authoring
  mistakes -- see `calibration.md`, "When the solution fails, suspect your
  data first".

This is SWE-bench's trick in miniature: its ground truth is the test the
developer already wrote, and the filter is that the test fails before the
patch and passes after. Whenever the domain admits a generator-and-deriver
shape, prefer it to a curated answer key.

## Mitigating leakage risk in real data

If using real data, these measures reduce (never eliminate) the risk that
a model has memorized the specific case:

- **Prefer modest-popularity sources.** A repo with 50-5,000 GitHub stars
  is far less likely to be heavily represented in training data than a
  framework-scale mega-repo (10k+ stars) with thousands of blog posts and
  tutorials about it. Below ~50 stars, credibility to a human reader
  suffers ("nobody uses this, does it even matter").
- **Avoid formally-cataloged incidents.** A bug with an assigned CVE/GHSA
  advisory is *more* likely to be indexed in security training data than
  an obscure, unlabeled bugfix commit -- despite intuition suggesting
  "official" sources are more obscure. If a candidate case has a formal
  advisory, that's a reason to skip it in favor of an unlabeled one that's
  otherwise equally good.
- **Avoid "textbook famous" patterns.** A case that's a canonical example
  used in thousands of blog posts and interview-prep articles (mutable
  default arguments, bare `except:`, off-by-one in a FizzBuzz-shaped loop)
  gets pattern-matched instantly regardless of whether the model actually
  reasoned about the code in front of it -- this saturates the case to
  near-zero discriminative power almost immediately. Prefer cases whose
  root cause requires actually reading the surrounding code, not just
  recognizing a category name.
- **Prefer more recent material** when the task's framing allows it (e.g.
  a live/upcoming event with inputs frozen before it happens) -- if the
  material postdates a model's training cutoff, leakage is structurally
  impossible, not just improbable. This is the strongest mitigation
  available when it fits the domain.
- **Document the residual risk plainly** in the task's README rather than
  imply the task is leakage-proof. State the mitigations taken and note
  that leakage is reduced, not eliminated -- an honest limitation beats an
  overclaimed guarantee.

## Licensing

If sourcing real content (code, text, data) from somewhere else, only use
permissively-licensed sources: MIT, Apache-2.0, BSD-3-Clause (for code) or
their content equivalents (CC BY, CC0). Reproducing even a small excerpt
under a more restrictive license, or from a source whose ToS forbids
redistribution, creates real legal exposure -- check `legal-ip-checklist.md`
before writing a single line of `gold.cases.json` if there's any doubt.

## Fidelity to the platform's positioning

TrapStreet is "GitHub + Speedrun for community AI repos" -- the audience
is non-technical industry workers evaluating tools for their own work, not
ML researchers. This should steer case selection, not just licensing:

- Prefer comparing **community-built tools/skills/repos** people
  actually see discussed online, over comparing raw frontier models
  against each other.
- Cases should be graspable in seconds by someone without an ML
  background, but hard enough to actually separate good solutions from
  weak ones -- avoid both trivia-trick esoterica and anything that reads
  as an academic benchmark question.
- Avoid setups that require a vendor-specific grading service, expert
  human curation per case, or anything that only works "if you already
  have access to X" -- the bar is "anyone can run this in any
  environment."

## Gold must come from a channel the shipped artifact does not carry

"Compute it, never author it" settles *how* to get the answer. It does not
settle *from where*, and the right source flips depending on what the
document is made of. Get this backwards and the task is correct by
construction for whichever pipeline shares your source.

| The answer lives in | Take gold from | Never from | Because |
|---|---|---|---|
| A digital table | reading the render by eye | the PDF's text layer | a text parser extracts the same bytes, so every parser-based solution is right by construction |
| A chart | measuring the pre-rasterisation vector geometry | your eye | the author's own eye-read of one panel was 1/4/5/4/1 where the geometry said 2/5/6/4/1 |

On `pdf_chart_reading` the figures are vector paths in the original release.
No parser reads a data point out of a path -- but `page.get_drawings()`
*measures* every bar and dot exactly, which is where that task's gold comes
from. Shipping the vector charts would therefore hand a geometry-reading
solution a perfect score for free, so the figure pages are **rasterised in
the shipped document**. The measurement channel exists for the author and is
removed from the artifact. Disclose the construction; it is the instrument,
not a trick.

## Check gold against something the document says about itself

A measured answer key needs a check that does not come from the same
measurement. The best ones are invariants the document states in prose:

- `pdf_chart_reading`: a footnote to table 1 reads "Eighteen participants
  submitted information in conjunction with the June 16-17, 2026, meeting;
  one of these 18 participants did not submit projections for 2028." Every
  panel of every figure must sum to that. The extractor asserts it and
  refuses to write a gold file that violates it -- which caught a real bug
  on the first run (a legend swatch counted as a panel).
- Two figures that encode the same variable in different chart types must
  agree bin for bin. Figure 2 (dots) and figure 3.E (histogram) did, across
  all four panels.
- A third-party publication of the same numbers, if one exists, is a free
  audit -- but only as a *check*. It is also an answer key for anyone whose
  solution fetches it, so record it under known limitations rather than
  hoping nobody looks.

Four independent confirmations is not overkill for a measured key. Three of
the four found nothing; the fourth found the bug.

## Verify no case is answerable from the parts you left readable

A mixed document (some pages text, some not) needs an explicit audit that the
readable half does not answer the questions, and a test that keeps it true.
On `pdf_chart_reading` table 1 reports medians, central tendencies and
ranges, never a count of participants -- so none of the twenty-two count
questions is reachable from text. The only figures stated in words are the
participant totals, and no case is allowed to answer with one of those. That
is a three-line test, and without it the audit rots the first time a case is
added.
