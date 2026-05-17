# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A single-file AI skill that distills a GitHub repository contributor's observable commit history into a reusable contributor skill file (`[username]/SKILL.md`). No scripts, no dependencies — just a SKILL.md that guides AI agents to do the work using git commands directly.

> [中文版 / Chinese version](README_zh_CN.md)

## What it does

Given a repository and a contributor name/email/username, the AI agent:

1. **Resolves identity** — scans `git log` for matching author/committer names and emails
2. **Collects evidence** — aggregates all commits for statistics, commit messages, and branch patterns; stratified diff sampling across time periods for coding style extraction
3. **Distills patterns** — identifies stable, observable behaviors: naming conventions, component patterns, state management, commit granularity
4. **Generates a skill file** — outputs a structured `[username]/SKILL.md` with actionable implementation rules and do/don't reference table

## How to use

Load `SKILL.md` into any AI coding agent (Claude Code, ChatGPT, Cursor, etc.), then ask:

```
Distill the contributor "Jane Zhang" from https://github.com/org/repo
```

Or for a local repo:

```
Distill the contributor "janezhang" from /path/to/local/repo, output to ./distilled
```

The agent will follow the SKILL.md workflow to run git commands, analyze history, and generate the output skill file.

## How it works

The SKILL.md contains a complete, step-by-step workflow:

- **Identity resolution** — how to scan git history and match contributors by name, email, or commit hash
- **Full statistics** — aggregates all commits for file frequency, directory distribution, extensions, commit message patterns, branch naming
- **Stratified diff sampling** — selects top 12 most-touched source files, picks one diff from each third of the timeline to capture style evolution
- **Pattern distillation** — maps evidence to concrete dimensions: naming, components, state management, error handling, commit strategy
- **Output template** — the exact structure of the generated contributor skill file
- **Security rules** — argument injection prevention and output sanitization

The AI agent executes each step using native git commands. No external scripts or dependencies required.

## Output structure

The generated `[username]/SKILL.md` includes:

| Section | Content |
|---|---|
| **Scope & Evidence** | Commit count, date range, identity, confidence level |
| **Tech Stack & Architecture** | Framework, libraries, directory responsibilities |
| **Naming & Typing** | Interface/type/variable/file naming conventions from diff analysis |
| **Component Patterns** | Memo strategy, displayName, props design, composition patterns |
| **State Management** | Server state, mutations, cache strategy, shared logic patterns |
| **Error & Edge Cases** | Loading, empty states, auth guards, error handling patterns |
| **Commit & Workflow** | Message style, change decomposition, branch strategy |
| **Quick Reference** | Do/don't table derived from strongest observed patterns |
| **Guardrails** | Overfitting prevention, privacy boundaries |

## Confidence levels

| Commits | Confidence | Meaning |
|---:|---|---|
| < 5 | **Low** | Treat all conclusions as tentative |
| 5-19 | **Medium** | Patterns may be concentrated in one area |
| 20+ | **High** | Reliable cross-area patterns |

## Project structure

```
github-contributor-distiller/
├── SKILL.md          # The entire skill — load this into any AI agent
├── LICENSE            # MIT
├── README.md          # You are here
└── README_zh_CN.md   # 中文版
```

## Requirements

- An AI coding agent that can run git commands (Claude Code, ChatGPT with code interpreter, Cursor, etc.)
- `git` available on the agent's PATH
- For GitHub URLs: network access (public repos) or configured git credentials (private repos)

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
