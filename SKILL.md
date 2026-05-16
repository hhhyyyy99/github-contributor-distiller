---
name: github-contributor-distiller
description: distill a github or local git repository contributor's observed commit history into a repo-specific contributor skill file. use when the user provides a repository url or local git path plus at least a contributor name, username, email, or commit hash, and wants the final output as [username]/SKILL.md rather than a packaged skill zip.
---

# GitHub Contributor Distiller

## Overview

Generate a repo-specific contributor skill at `[username]/SKILL.md` by scanning a Git repository's commit history for a named contributor and distilling observable coding, testing, commit, and review patterns.

The output is a single target skill file by default: `[username]/SKILL.md`. Do not package the generated target skill unless the user explicitly asks for a zip.

## Minimum Input

Require a repository and at least one contributor identifier.

Accept repository input as either:
- A GitHub repository URL, for example `https://github.com/org/repo`
- A local git repository path

Accept contributor input as one or more of:
- Contributor display name, such as `Jane Zhang`
- GitHub username, such as `janezhang`
- Email address
- Commit hash, if the user wants to anchor identity discovery from a known commit

If the user provides only a contributor name but no repository, ask for the repository. If the repository is provided and only a name is provided, proceed by resolving the name against commit history.

## Workflow

1. **Resolve the repository**
   - For a local path, verify it is inside a git work tree.
   - For a GitHub URL, clone it with git. Public repositories should work without credentials; private repositories require the user's environment to already have git credentials or token-based access configured.
   - If a GitHub connector is available, use it only to verify repo metadata or resolve ambiguity; the git history is still the source of truth for style distillation.

2. **Resolve contributor identity**
   - Search `author.name`, `author.email`, `committer.name`, and `committer.email` across history.
   - Treat multiple emails for the exact same display name as aliases for the same contributor unless evidence suggests otherwise.
   - If the name is ambiguous, stop and show candidates rather than guessing.
   - Prefer exact name, exact email, or exact username/email-local-part matches over substring matches.

3. **Collect evidence**
   - Gather recent matching commits, changed paths, extensions, top-level directories, numstat additions/deletions, commit subjects, test/doc/config touches, and representative diff samples.
   - Keep evidence bounded. Do not include large raw code excerpts in the final `[username]/SKILL.md`.
   - Use only observable repository behavior. Do not infer personal traits, motives, seniority, or private preferences.

4. **Distill patterns**
   - Identify stable repository-facing patterns: modules commonly edited, file placement, language/framework footprint, test discipline, commit granularity, message style, error handling, typing, docs, migrations, config, and review checks.
   - Separate high-confidence findings from weak signals. Phrase weak findings as "often", "appears to", or "based on the sampled commits".

5. **Render final output**
   - Generate exactly `[username]/SKILL.md` as the final user-facing artifact.
   - The `[username]` directory should be a sanitized lowercase slug derived from the GitHub username when known, otherwise from the contributor name.
   - The generated `SKILL.md` must be a usable skill entrypoint with YAML frontmatter containing only `name` and `description`.

## Scripted Distillation

Use `scripts/distill_contributor_skill.py` for the repeatable scan and first draft.

Basic usage:

```bash
python scripts/distill_contributor_skill.py \
  --repo https://github.com/org/repo \
  --contributor "Jane Zhang" \
  --out ./distilled
```

This writes:

```text
distilled/jane-zhang/SKILL.md
```

Use a fixed output directory name when the user provides a GitHub username:

```bash
python scripts/distill_contributor_skill.py \
  --repo /path/to/repo \
  --contributor "Jane Zhang" \
  --username janezhang \
  --out ./distilled
```


When the user provides a known commit hash to anchor identity resolution, pass it with `--commit`:

```bash
python scripts/distill_contributor_skill.py \
  --repo /path/to/repo \
  --contributor "Jane Zhang" \
  --commit abc1234 \
  --username janezhang \
  --out ./distilled
```

For deeper manual refinement, ask the script to write bounded evidence files, then edit only the generated `SKILL.md` before presenting the final answer:

```bash
python scripts/distill_contributor_skill.py \
  --repo /path/to/repo \
  --contributor "Jane Zhang" \
  --username janezhang \
  --out ./distilled \
  --write-evidence
```

When evidence files exist, use them internally to improve the final `SKILL.md`, but do not present them as the final output unless the user asks.

## Generated `[username]/SKILL.md` Requirements

The generated target skill must include these sections:

1. `Overview` - what repository and contributor profile this skill captures.
2. `Scope and evidence` - commit count, time range, identity aliases, and uncertainty.
3. `How to use this skill` - when another ChatGPT should apply it.
4. `Repository orientation` - common directories, file types, and modules touched.
5. `Contributor working style` - change size, testing/doc habits, commit message style.
6. `Implementation rules` - concrete guidance for making changes in this repo.
7. `Testing and validation` - inferred tests or validation behavior from history.
8. `Review checklist` - checks to run before considering a change consistent with the profile.
9. `Guardrails` - avoid overfitting, do not mimic private identity traits, and prioritize current repo instructions over historical style.

## Quality Rules

- Prefer concise, actionable rules over biography.
- Ground every strong statement in commit evidence.
- Never claim the contributor "always" does something unless the evidence is overwhelming.
- Do not expose secrets, tokens, or private data found in history.
- Do not paste large code excerpts into the generated skill.
- Keep the generated skill useful even when the contributor has few commits by emphasizing uncertainty and repository conventions.
- If the contributor has fewer than 5 matching commits, label the output as low-confidence.
