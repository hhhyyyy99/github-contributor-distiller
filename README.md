# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A single-file AI skill that distills a GitHub repository contributor's observable commit history into a reusable contributor skill file (`[username]/SKILL.md`). No scripts, no dependencies — just a SKILL.md that guides AI agents to do the work using git commands directly.

## What it does

Given a repository and a contributor name/email/username, the AI agent:

1. **Resolves identity** — scans `git log` for matching author/committer names and emails
2. **Collects evidence** — gathers commit history, changed paths, file types, change sizes, commit message patterns
3. **Distills patterns** — identifies stable, observable behaviors: modules commonly edited, testing discipline, commit granularity, naming conventions
4. **Generates a skill file** — outputs a structured `[username]/SKILL.md` with actionable implementation rules, review checklists, and guardrails

## How to use

Load `SKILL.md` into any AI coding agent (Claude, ChatGPT, Cursor, etc.), then ask:

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
- **Evidence collection** — what git commands to run and what patterns to extract
- **Pattern distillation** — how to translate raw evidence into actionable guidance
- **Output template** — the exact structure of the generated contributor skill file
- **Security rules** — argument injection prevention and output sanitization

The AI agent executes each step using native git commands. No external scripts or dependencies required.

## Output structure

The generated `[username]/SKILL.md` includes:

| Section | Content |
|---|---|
| **Overview** | Repository and contributor context |
| **Scope and evidence** | Commit count, date range, identity aliases, confidence level |
| **How to use this skill** | When and how to apply the profile |
| **Repository orientation** | Common directories, file types, modules touched |
| **Contributor working style** | Change size, test/doc habits, commit message patterns |
| **Implementation rules** | Concrete rules for code placement, naming, error handling |
| **Testing and validation** | Inferred test behavior from history |
| **Review checklist** | Pre-finalization checks |
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
├── SKILL.md      # The entire skill — load this into any AI agent
├── LICENSE        # MIT
└── README.md      # You are here
```

## Requirements

- An AI coding agent that can run git commands (Claude Code, ChatGPT with code interpreter, Cursor, etc.)
- `git` available on the agent's PATH
- For GitHub URLs: network access (public repos) or configured git credentials (private repos)

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
