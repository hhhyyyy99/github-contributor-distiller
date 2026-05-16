# Contributor Distillation Rubric

Distill only behavior that is observable from repository history.

## Identity resolution

Inspect all of these fields:
- `author.name`
- `author.email`
- `committer.name`
- `committer.email`

Prefer exact matches. Treat same-name multiple-email identities as aliases, but ask the user to choose when a substring query matches multiple distinct names.

## Evidence dimensions

Collect and summarize:
- Commit count and active date range
- Top changed directories and files
- File extensions and inferred languages/frameworks
- Test, docs, config, migration, and CI touches
- Commit subject patterns and conventional commit usage
- Typical change size by files changed and additions/deletions
- Whether changes are localized or cross-cutting
- Repeated modules, APIs, package boundaries, or test locations

## Distillation dimensions

Translate evidence into practical guidance:
- Where to place new code
- How to keep changes small or structured
- Whether to add or update tests by default
- How to name files/functions/classes based on repo patterns
- How to handle errors, logging, typing, comments, configuration, docs, and migrations
- How to write commit summaries if the user asks for commits
- How to review work before finalizing

## Confidence labeling

Use low confidence when fewer than 5 commits match.
Use medium confidence when 5-19 commits match or the evidence is concentrated in one area.
Use high confidence when 20+ commits match across meaningful repository areas.

Avoid absolute wording unless a pattern is near-universal in the evidence.
