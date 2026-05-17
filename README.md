# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**A contributor's git history tells you how they code. This tool extracts that story into a file your AI can read.**

Point it at any repo and a contributor name. It reads their full commit history — every diff, every message, every branch — and outputs a structured style guide (`[username]/SKILL.md`) that any AI coding agent can load and follow.

No scripts. No dependencies. One SKILL.md file.

> [中文版 / Chinese version](README_zh_CN.md)

## See it in action

Run this in any AI agent:

```
Distill the contributor "Jane Zhang" from https://github.com/org/repo
```

The agent scans git history and generates `janezhang/SKILL.md`. Here's what the output looks like (abbreviated):

```markdown
## Naming & Typing

- PascalCase for interfaces: `UserProfile`, `CartItem`, `OrderSummary`
- Prefixed with `I` only for API boundaries: `IAuthService`
- Hook return types always explicit: `useCart(): { items, addItem, removeItem, total }`
- File names match default export: `useCart.ts`, `UserProfile.tsx`

## Component Patterns

- Heavy use of `useMemo` for derived state, rarely `useCallback` unless passing to memoized children
- Props destructured inline: `function UserCard({ name, avatar, onClick }: UserCardProps)`
- No `displayName` — relies on function name inference
- Prefers compound components over prop-heavy ones

## State Management

- Server state via custom hooks wrapping fetch — no Redux, no Zustand for remote data
- Local state with `useState`; `useReducer` only when 3+ related toggles
- Optimistic updates for mutations, rollback on error

## Commit Strategy

- Subject under 50 chars, imperative mood: `fix: reset cart on logout`
- One logical change per commit; mechanical renames get their own commit
- Body used only for "why", never "what"
```

Now any AI agent working on this repo can match Jane's patterns instead of inventing its own style.

## How to use

Load `SKILL.md` into any AI coding agent (Claude Code, ChatGPT, Cursor, etc.), then ask:

```
Distill the contributor "Jane Zhang" from https://github.com/org/repo
```

Or for a local repo:

```
Distill the contributor "janezhang" from /path/to/local/repo, output to ./distilled
```

The agent follows the SKILL.md workflow: run git commands, analyze history, generate the output file.

## What it does

Give it a repository and a contributor (name, email, or username). The agent scans `git log` to match the identity, aggregates all commits for stats and message patterns, picks stratified diff samples across the timeline, then distills naming conventions, component patterns, state management, and commit strategy into a structured `[username]/SKILL.md` with a do/don't reference table.

## How it works

SKILL.md is a self-contained workflow. The agent runs these steps:

**Identity resolution** — scans git history, matches contributors by name, email, or commit hash.

**Full statistics** — aggregates every commit: file frequency, directory distribution, extensions, message patterns, branch naming.

**Stratified diff sampling** — picks the 12 most-touched source files, takes one diff from each third of the timeline to capture how the contributor's style evolved.

**Pattern distillation** — maps evidence to naming, components, state management, error handling, and commit strategy.

**Output template** — defines the structure of the generated contributor skill file.

**Security rules** — argument injection prevention and output sanitization.

Everything runs on native git commands. No scripts, no dependencies.

## Output structure

The generated file has these sections:

| Section | Content |
|---|---|
| Scope & Evidence | Commit count, date range, identity, confidence level |
| Tech Stack & Architecture | Framework, libraries, directory layout |
| Naming & Typing | Interface, type, variable, and file naming conventions |
| Component Patterns | Memo strategy, displayName, props, composition |
| State Management | Server state, mutations, caching, shared logic |
| Error & Edge Cases | Loading, empty states, auth guards |
| Commit & Workflow | Message style, change decomposition, branching |
| Quick Reference | Do/don't table from the strongest observed patterns |
| Guardrails | Overfitting prevention, privacy boundaries |

## Confidence levels

| Commits | Confidence | Meaning |
|---:|---|---|
| < 5 | **Low** | Treat all conclusions as tentative |
| 5-19 | **Medium** | Patterns may be concentrated in one area |
| 20+ | **High** | Reliable cross-area patterns |

## What this tool does NOT do

- **It doesn't judge code quality.** It observes patterns, not whether they're "good."
- **It doesn't read minds.** It can only extract what's visible in diffs and commit messages. Private Slack discussions, code review comments, and verbal conventions are out of reach.
- **It doesn't freeze a person in time.** Developers evolve. Re-run the distillation periodically to capture drift.
- **It doesn't replace code review.** The output is a style reference for AI agents, not a human-readable team handbook.

## Project structure

```
github-contributor-distiller/
├── SKILL.md          # The entire skill — load this into any AI agent
├── LICENSE            # MIT
├── README.md          # You are here
└── README_zh_CN.md   # 中文版
```

## Requirements

- An AI coding agent that can run git commands (Claude Code, ChatGPT, Cursor, etc.)
- `git` installed
- For GitHub URLs: network access (public repos) or git credentials (private repos)

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)

## Friends

[Linux.do](https://linux.do/)
