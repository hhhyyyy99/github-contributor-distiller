---
name: github-contributor-distiller
description: distill a github or local git repository contributor's observed commit history into a reusable contributor skill file. use when the user provides a repository url or local git path plus at least a contributor name, username, email, or commit hash.
---

# GitHub Contributor Distiller

## Overview

Scan a git repository's commit history for a named contributor and distill observable coding, testing, commit, and review patterns into a contributor skill file.

The output is a single markdown file: `[username]/SKILL.md`. Do not package it unless the user explicitly asks.

## Minimum Input

Require a repository and at least one contributor identifier.

**Repository** — accept either:
- A GitHub repository URL (e.g. `https://github.com/org/repo`)
- A local git repository path

**Contributor** — accept one or more of:
- Display name (e.g. `Jane Zhang`)
- GitHub username (e.g. `janezhang`)
- Email address
- Commit hash (to anchor identity from a known commit)

If only a name is given without a repo, ask for the repo. If the repo is given and only a name, proceed by resolving against commit history.

## Workflow

Execute each step using git commands. Do NOT use any external scripts.

### Step 1: Resolve the repository

```bash
# For a local path, verify it is inside a git work tree:
git -C <local_path> rev-parse --show-toplevel

# For a GitHub URL, clone it:
git clone --quiet <url> /tmp/contributor-distiller-<name>
```

For public repos, no credentials needed. For private repos, the user's environment must have git credentials or token-based access configured.

If a GitHub CLI or connector is available, use it only to verify repo metadata or resolve ambiguity. The git history is always the source of truth.

### Step 2: Resolve contributor identity

Run these commands to scan ALL identities in the repo history:

```bash
git -C <repo> log --all --format="%aN|%aE|%cN|%cE"
```

Parse the output to build a list of unique (name, email) pairs from both author and committer fields. Treat multiple emails for the same display name as aliases for the same contributor unless evidence suggests otherwise.

**Matching priority** (highest to lowest):
1. Exact email match
2. Exact name match
3. Exact email local-part match (the part before @)
4. Case/space-insensitive name match
5. Email local-part substring match
6. Name substring match

If the query is ambiguous and matches multiple distinct people, STOP and show a candidate table. Do NOT guess.

**If a commit hash is provided**, resolve identity from that commit:
```bash
git -C <repo> show -s --format="%aN|%aE|%cN|%cE" <hash>
```

Use the author identity from this commit to anchor the search.

### Step 3: Collect evidence

Once identity is resolved, gather matching commits:

```bash
git -C <repo> log --all --format="%H|%ad|%s" --date=short --author="<name_or_email>"
```

Limit to 80 most recent matching commits.

For each commit, collect:

```bash
# Changed files with additions/deletions:
git -C <repo> show --numstat --format= <hash>
```

Aggregate across all matching commits:
- Commit count and active date range
- Top changed directories and files (by frequency)
- File extensions and inferred languages/frameworks
- Test, docs, config, migration, and CI file touches
- Commit subject patterns and conventional commit usage (feat:, fix:, refactor:, etc.)
- Typical change size: median files changed, average additions/deletions
- Whether changes are localized (1-2 files) or cross-cutting (5+ files)
- Repeated modules, APIs, package boundaries, or test locations

**Keep evidence bounded.** Do not include large raw code excerpts in the final output.

### Step 4: Distill patterns

Translate evidence into practical guidance:

| Evidence | Guidance |
|---|---|
| Top directories | Where to place new code |
| Median files/commit | How to scope changes |
| Test file touches | Whether to add/update tests by default |
| File naming patterns | Naming conventions for files/functions/classes |
| Error handling in diffs | Error handling style |
| Type annotations | Typing discipline |
| Commit subjects | Commit message style |
| Docs file touches | When to update documentation |

**Confidence labeling:**
- Fewer than 5 commits: **low confidence** — treat all conclusions as tentative
- 5-19 commits or single-area concentration: **medium confidence**
- 20+ commits across meaningful areas: **high confidence**

Avoid absolute wording unless a pattern is near-universal. Phrase weak findings as "often", "appears to", or "based on the sampled commits".

### Step 5: Render output

Create the directory and write the skill file:

```
<out_dir>/<username>/SKILL.md
```

The `<username>` should be a sanitized lowercase slug derived from the GitHub username when known, otherwise from the contributor name. Strip everything except lowercase alphanumeric and hyphens. Max 64 characters.

---

## Output Template

Use this exact structure for the generated `[username]/SKILL.md`:

````markdown
---
name: <username-slug>
description: repo-specific contributor guidance distilled from git commit history. use when working in <repo-name> and asked to implement, modify, review, or explain code in a style consistent with <contributor>'s observed contributions.
---

# <Contributor> contributor skill for <repo>

## Overview

Use this skill when working in `<repo>` and the user wants changes, review, or explanations aligned with `<contributor>`'s observed contribution style in this repository.

This is a repository-facing style guide, not a biography. It summarizes observable commit behavior only.

## Scope and evidence

- Repository: <repo>
- Contributor identity: <names/emails/usernames>
- Commit sample: <n> commits from <first-date> to <last-date>
- Confidence: <high/medium/low>
- Limitations: <sampling notes>

## How to use this skill

Apply this skill after reading the user's request, current repository instructions, project docs, and relevant source files. Use it to bias decisions about change scope, file placement, tests, and review habits. Do not use it to override explicit user instructions or current code conventions.

## Repository orientation

<Common directories, file types, modules, and responsibilities. List top directories, extensions, languages, and file roles.>

## Contributor working style

<Observed change size, commit message style, test/doc/config habits. Include specific numbers from the evidence.>

Representative sampled commit subjects:

<10 sample commit subjects>

## Implementation rules

<Concrete rules for editing, code placement, naming, error handling, typing, comments, preserving existing patterns.>

## Testing and validation

- Run the repository's documented test, lint, typecheck, or build commands when available.
- When the change affects behavior, update nearby tests even if the sampled history has weak test evidence.
- If tests are hard to run, clearly state what was and was not validated.
- Keep generated changes focused enough that failures can be traced to the requested work.

## Review checklist

- The changed files are in the expected repository area for this kind of work.
- The diff avoids unrelated formatting, renames, or refactors.
- Naming, imports, typing, logging, comments, and error handling match surrounding code.
- Behavior changes include appropriate tests or an explicit validation note.
- Docs/config/CI updates are included when the code change makes them necessary.
- Commit messages mirror the repository's recent style.

## Guardrails

- Do not infer personal traits, intent, availability, seniority, or private preferences from commit history.
- Do not copy large historical code excerpts into responses.
- Treat this profile as a set of tendencies, not absolute rules.
- When evidence is sparse or conflicting, say so and prioritize the current codebase.
````

---

## Quality Rules

- Prefer concise, actionable rules over biography.
- Ground every strong statement in commit evidence.
- Never claim the contributor "always" does something unless the evidence is overwhelming.
- Do not expose secrets, tokens, or private data found in history.
- Do not paste large code excerpts into the generated skill.
- Keep the generated skill useful even when the contributor has few commits by emphasizing uncertainty and repository conventions.
- Sanitize any git metadata (commit subjects, author names, emails) embedded in the output: strip HTML comments, script tags, and control characters.

## Security

- When running `git` commands with user-supplied values, always use `--` before positional arguments (branch names, commit hashes) to prevent argument injection.
- Never use `shell=True` or pipe user input through a shell.
- Treat the repository URL as untrusted — use it only as a positional argument to `git clone`.
