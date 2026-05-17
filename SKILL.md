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

Two phases. Phase 2 depends on Phase 1 results.

#### Phase 1: Full statistics

Collect ALL matching commits — do not limit or sample at this stage.

```bash
# All commit subjects and dates:
git -C <repo> log --all --format="%H|%ad|%s" --date=short --author="<name_or_email>"

# All numstat in one pass (much faster than per-commit git show):
git -C <repo> log --all --numstat --format="" --author="<name_or_email>"

# All branch references:
git -C <repo> log --all --format="%D" --author="<name_or_email>"

# All full commit messages (subject + body):
git -C <repo> log --all --format="%H|%ad|%B---MSG_SEP---" --date=short --author="<name_or_email>" --no-merges
```

Aggregate across ALL matching commits:
- Commit count (total, non-merge, merge) and active date range
- Top changed directories and files (by frequency)
- File extensions and inferred languages/frameworks
- Test, docs, config, migration, and CI file touches
- Commit subject patterns and conventional commit usage (feat:, fix:, refactor:, etc.)
- Typical change size: median files changed, average additions/deletions
- Whether changes are localized (1-2 files) or cross-cutting (5+ files)
- Repeated modules, APIs, package boundaries, or test locations
- Branch naming patterns
- Commit message language, body usage, tone

#### Phase 2: Diff sampling (stratified)

From Phase 1, select the **top 12 most-touched source files** (exclude generated files, i18n JSON, lock files, package.json, and other non-handwritten artifacts). If fewer than 12 qualifying files exist, use all of them.

For each selected file, retrieve diffs from **3 different time periods** to capture evolution:

```bash
# For each file, get all commit hashes by this contributor:
git -C <repo> log --all --format="%H|%ad" --date=short --author="<name_or_email>" -- <file>
```

From the list, pick one hash from the **earliest third**, one from the **middle third**, and one from the **most recent third**. This ensures patterns are captured across the full timeline, not just recent work.

```bash
# Then for each selected hash:
git -C <repo> show --format="" <hash> -- <file>
```

Cap total diff output at ~2000 lines. If a single diff exceeds 250 lines, truncate it to the first 250 lines.

From the sampled diffs, extract:
- **Naming conventions**: interface/type/variable/function/class naming patterns (I-prefix, camelCase, PascalCase, etc.)
- **Component patterns**: memo usage, displayName, props design, component decomposition
- **State management**: query/mutation patterns, cache strategies, optimistic updates
- **Error handling**: guard patterns, loading states, empty states, error boundaries
- **Import organization**: grouping, ordering, alias usage
- **Typing discipline**: interface vs type, explicit vs inferred, generic usage
- **Comment style**: JSDoc, inline comments, TODO markers
- **Code density**: single-line vs multi-line expressions, early returns, destructuring depth

**Keep evidence bounded.** Do not include large raw code excerpts in the final output.

### Step 4: Distill patterns

Translate evidence into the dimensions used in the output template:

| Evidence source | Output dimension |
|---|---|
| Diff: naming patterns | Naming & Typing |
| Diff: component structure, memo, props | Component Patterns |
| Diff: query/mutation/cache patterns | State Management |
| Diff: guards, loading, empty states | Error & Edge Cases |
| Numstat: files/commit, co-change patterns | Change Decomposition |
| Commit messages: format, language, body | Commit & Workflow |
| Numstat: directories, extensions | Tech Stack & Architecture |

**Confidence labeling:**
- Fewer than 5 non-merge commits: **low confidence** — treat all conclusions as tentative
- 5-19 non-merge commits or single-area concentration: **medium confidence**
- 20+ non-merge commits across meaningful areas: **high confidence**

**Evidence binding:** Every rule in the output must be traceable to specific observed patterns. If you cannot point to evidence, do not state it as a rule. Phrase weak findings as "often", "appears to", or "based on the sampled commits".

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
description: contributor coding style for <repo-name>. distilled from <n> commits by <contributor>. use when implementing, modifying, or reviewing code in this repository to match <contributor>'s observed patterns.
---

# <Contributor> — <Repo>

## Scope & Evidence

| Field | Value |
|---|---|
| Repository | `<repo>` |
| Identity | `<name> <primary email>` |
| Commits sampled | <n> (<n> non-merge) from <first-date> to <last-date> |
| Diff files sampled | <n> source files |
| Confidence | <high/medium/low> |

<If low or medium confidence, state what areas are well-covered vs uncertain.>

## Tech Stack & Architecture

<Framework, language, key libraries, path aliases, build tools — inferred from touched file extensions and imports.>

**Directory responsibilities:**
- `<dir/>` — <what this directory holds>
- `<dir/>` — <what this directory holds>
- ...

<Only list directories this contributor actually touches. Skip boilerplate directories.>

## Coding Style

### Naming & Typing

<Concrete rules extracted from diff sampling. Each rule must have an observed pattern.>

- **Interfaces**: <pattern, e.g. "I-prefix (IProps, IOptions, IActionVars)">
- **Types vs interfaces**: <preference>
- **Functions**: <casing, verb patterns>
- **Variables**: <casing, abbreviation habits>
- **Files**: <naming convention for component files, hook files, util files>

### Component Patterns

<Component architecture rules from diff sampling.>

- **Memo strategy**: <when/how memo() is used>
- **displayName**: <whether set, pattern>
- **Props design**: <interface shape, destructuring, defaults>
- **Composition**: <how components are composed — children, render props, hooks>
- **Component size**: <typical lines per component>

### State Management

<State and data flow patterns from diff sampling.>

- **Server state**: <TanStack Query / SWR / other — usage patterns>
- **Mutations**: <how mutations are structured, optimistic updates>
- **Cache strategy**: <staleTime, invalidation patterns>
- **Local state**: <useState, useReducer, context usage patterns>
- **Shared logic**: <hook extraction patterns — when and how>

### Error & Edge Cases

<How this contributor handles error states, loading, empty, and edge cases.>

- **Loading**: <skeleton, spinner, disabled UI>
- **Empty states**: <component used, messaging pattern>
- **Auth guards**: <guest mode, login prompts>
- **Error boundaries**: <try/catch, error states, fallback UI>

## Commit & Workflow

### Message Style

- **Format**: <conventional commit strictness level>
- **Language**: <English / Chinese / mixed>
- **Scope usage**: <when scope is included, format>
- **Body usage**: <never / for breaking changes / frequent>
- **Tone**: <imperative / descriptive, terse / verbose>

### Change Decomposition

- **Typical commit size**: <median files changed>
- **Granularity**: <single-concern vs multi-concern commits>
- **Refactor approach**: <inline vs separate commit, hook extraction triggers>
- **Feature scope**: <how a feature is broken into commits>

### Branch Strategy

- **Naming**: <pattern, e.g. `feature/<name>/<topic>`>
- **Merge style**: <merge commits / squash / rebase>
- **Integration flow**: <main → dev → test → pre or other>

## Quick Reference

<Concise do/don't table. Maximum 8 rows. Derived from the strongest observed patterns.>

| Do | Don't |
|---|---|
| <observed positive pattern> | <observed anti-pattern> |
| ... | ... |

## Guardrails

- Treat these patterns as tendencies, not absolute rules.
- When evidence is sparse or conflicting, prioritize the current codebase over this profile.
- Never copy large historical code excerpts into responses.
````

---

## Quality Rules

- **Evidence binding**: Every rule must trace to a specific observed pattern from commit history or diff sampling. No speculation.
- **Concise and actionable**: Prefer short, concrete rules over prose descriptions. The output will be consumed by AI agents, not read by humans for fun.
- **No biography**: Do not describe the contributor's career, role, seniority, or personality. Only observable code behavior.
- **Confidence-aware**: Fewer than 5 commits → all rules are tentative. Fewer than 20 commits → caveat concentrated areas. 20+ commits → state patterns with confidence.
- **No secrets**: Do not expose tokens, private data, or internal URLs found in history.
- **No large excerpts**: Do not paste large code blocks into the generated skill. Summarize patterns instead.
- **Sanitize metadata**: Strip HTML comments, script tags, and control characters from any git metadata embedded in the output.
- **Deduplicate**: If the contributor has multiple email aliases, consolidate all evidence under one profile. Do not split findings across aliases.

## Security

- When running `git` commands with user-supplied values, always use `--` before positional arguments (branch names, commit hashes) to prevent argument injection.
- Never use `shell=True` or pipe user input through a shell.
- Treat the repository URL as untrusted — use it only as a positional argument to `git clone`.
