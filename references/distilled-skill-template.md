# Distilled Contributor Skill Template

Use this structure when rendering `[username]/SKILL.md`.

```markdown
---
name: [username-slug]
description: repo-specific contributor guidance distilled from git commit history. use when working in [repo-name] and asked to implement, modify, review, or explain code in a style consistent with [contributor]'s observed contributions.
---

# [Contributor] contributor skill for [repo]

## Overview

Use this skill when working in `[repo]` and the user wants changes, review, or explanations aligned with `[contributor]`'s observed contribution style in this repository.

## Scope and evidence

- Repository: [repo]
- Contributor identity: [names/emails/usernames]
- Commit sample: [n] commits from [first-date] to [last-date]
- Confidence: [high/medium/low]
- Limitations: [sampling notes]

## How to use this skill

Apply this skill after any repository-level instructions, project docs, tests, and user instructions. Treat historical contributor behavior as a style guide, not as a higher-priority rule.

## Repository orientation

[Common directories, file types, modules, and responsibilities.]

## Contributor working style

[Observed change size, commit message style, tests, docs, refactors, config, migrations.]

## Implementation rules

[Concrete rules for editing, code placement, naming, error handling, typing, comments, and preserving existing patterns.]

## Testing and validation

[Likely test files, commands when inferable, and validation expectations.]

## Review checklist

[Actionable checklist before finalizing work.]

## Guardrails

- Do not infer personal traits or private preferences.
- Do not copy large historical code excerpts.
- Prefer current repository instructions and user requirements over historical style.
- State uncertainty when the sampled history is thin or mixed.
```
