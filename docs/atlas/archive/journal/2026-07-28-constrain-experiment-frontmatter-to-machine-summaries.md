---
date: 2026-07-28
slug: constrain-experiment-frontmatter-to-machine-summaries
project: Atlas
tags: [entities, templates, validate, experiments]
status: closed
opened: 2026-07-28 20:25
closed: 2026-07-28 22:56
verification-result: passed
related: []
---

# Constrain experiment frontmatter to machine summaries

## Context

A dogfood example from another project (E-033 there) showed the experiment entity's failure mode: the template gives the same content two homes — frontmatter fields (hypothesis/config/result/conclusion) and same-named body sections — and validate.py only presence-checks the frontmatter keys, so the agent fills frontmatter with multi-paragraph prose (80% of the file), duplicates some of it in the body, and punts the body Conclusion with a "见frontmatter" pointer. Meanwhile orient.py reads the body Hypothesis section, not the frontmatter fields, so the machine-facing copy is the one nobody reads. Fix direction agreed with the user: frontmatter fields shrink to one-line machine summaries (enforced by a length cap in validate.py), the body is the canonical prose, and "见 frontmatter / see frontmatter" pointer text in bodies becomes a validate error. Template comments updated to state the constraint; changes land in both template copies and both validate.py copies (repo source + installed skill).

## Work log

### 2026-07-28 20:30
Implemented the single-owner split for experiment entities. validate.py (skills/atlas-entity/scripts/, symlink-deployed): E content fields (hypothesis/config/result/conclusion) now walk all string leaves and reject any over 300 chars; all entity bodies now reject "见 frontmatter"/"see frontmatter" pointer text (bodies loaded alongside meta in load_all). experiment.md template (templates/_templates/ + docs/atlas/_templates/, kept identical): frontmatter comment block states the one-line-summary constraint and both validate checks; per-field hints (one falsifiable sentence / key params / key numbers / one-two sentence verdict); body Conclusion comment demands full prose — worded to avoid containing the banned literal, which the check itself caught on first run (fresh entities carry template comments in the body). schemas.md: config/result notes tightened, cap + pointer-ban paragraph added under the E table. Tests: 4 new (fresh E passes; overlong scalar conclusion fails; overlong nested result value fails; both pointer variants fail) on an experiment_project fixture stacked on constitution_project — the plain project fixture leaves PROJECT.md pointers dangling and never passed validate. 30/30 green; real store validates OK (28 entities).

## Close

Experiment frontmatter fields constrained to one-line machine summaries (300-char cap on string leaves of hypothesis/config/result/conclusion) and bodies banned from pointing back at frontmatter — both enforced by validate.py, stated in the template comments and schemas.md. Choice recorded as D-023 (status active, triage pending). Verification: 4 new pytest cases covering pass/fail modes, full suite 30/30 green; real store validates OK. The check proved itself twice during the work by catching the template's own body comment and D-023's own Context quoting the banned literal.
