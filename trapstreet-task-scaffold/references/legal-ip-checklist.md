# Legal / IP checklist -- decide before writing gold.cases.json, not after

Some real tasks in this repo exist only in a local, gitignored working
tree because their source material can't legally be published. Deciding
this *before* building the task avoids the much worse alternative:
building a full public task, then discovering a licensing/liability
problem and having to un-publish it.

## Questions to ask before sourcing any real material

1. **What's the license or ToS of the source?** Reddit's ToS forbids
   redistribution of post content -- a task built on scraped Reddit posts
   cannot be published even with attribution. Similarly, a site's ToS
   might forbid automated scraping regardless of what's technically
   accessible.
2. **Is there a copyright holder who could object?** Republishing curated
   data (e.g. a proprietary drug-interaction database) can infringe the
   compiler's copyright even if the underlying facts are public domain.
3. **Could getting a case wrong create real-world harm if someone treated
   the task's answer as authoritative?** A medical/legal/safety-domain
   task carries liability risk distinct from a coding task -- if a
   published eval implies "this verdict is correct" and it's wrong in a
   way that matters, that's a different risk category than a wrong bug
   report.
4. **Does the source material belong to someone else's business?**
   Production code, internal documents, or data from a current or former
   employer is their IP, not yours to publish, even anonymized in many
   cases -- and even fully anonymized, check whether the *fact pattern*
   itself (not just the identifiers) is confidential.

## If any answer raises a real concern

Keep the task **local-only**: build it exactly the same way, but add its
directory to `.gitignore` rather than committing it. This preserves the
option to build now and decide on publication (or a scrubbed/synthetic
replacement) later, without ever having published something that
shouldn't have been public even briefly -- a `git revert` doesn't undo the
fact that a commit was pushed to a public remote at some point.

## If genuinely unsure

Ask the person actually accountable for the platform's legal exposure
before publishing -- this is not a call to make unilaterally when the
answer isn't obvious. It's fine to build the task fully (including
running it locally) while that question is open; just don't `git push` to
a public repo until it's resolved.
