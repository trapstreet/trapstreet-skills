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
