# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

Distill a GitHub repository contributor's observable commit history into a reusable **contributor skill file** (`[username]/SKILL.md`). The output is a structured style guide that captures how a specific contributor writes code, commits, tests, and reviews — grounded entirely in real git evidence, not speculation.

## What it does

Given a repository and a contributor name/email/username, this tool:

1. **Resolves identity** — scans `git log` for matching author/committer names and emails
2. **Collects evidence** — gathers commit history, changed paths, file types, change sizes, commit message patterns
3. **Distills patterns** — identifies stable, observable behaviors: modules commonly edited, testing discipline, commit granularity, naming conventions
4. **Generates a skill file** — outputs a structured `[username]/SKILL.md` with actionable implementation rules, review checklists, and guardrails

## Quick start

```bash
# From a GitHub URL
python scripts/distill_contributor_skill.py \
  --repo https://github.com/org/repo \
  --contributor "Jane Zhang" \
  --out ./distilled

# From a local repo
python scripts/distill_contributor_skill.py \
  --repo /path/to/local/repo \
  --contributor "Jane Zhang" \
  --username janezhang \
  --out ./distilled
```

Output: `distilled/janezhang/SKILL.md`

## Usage

```
usage: distill_contributor_skill.py [-h] --repo REPO --contributor CONTRIBUTOR
                                    [--username USERNAME] [--email EMAIL]
                                    [--commit COMMIT] [--branch BRANCH]
                                    [--since SINCE] [--until UNTIL]
                                    [--max-commits N] [--out DIR]
                                    [--write-evidence]
```

### Key options

| Flag | Description |
|---|---|
| `--repo` | GitHub URL or local git repository path (required) |
| `--contributor` | Name, username, or email to search in commit history (required) |
| `--username` | Output directory slug; defaults to sanitized contributor name |
| `--email` | Exact email to disambiguate identity; can be repeated |
| `--commit` | Commit hash to anchor identity resolution; can be repeated |
| `--branch` | Branch to scan; defaults to `--all` |
| `--since` / `--until` | Date range filter for git log |
| `--max-commits` | Max commits to analyze (default: 80) |
| `--out` | Output parent directory (default: current dir) |
| `--write-evidence` | Also emit `analysis.json` and `diff_samples.md` for refinement |

### Examples

**Anchor from a known commit:**
```bash
python scripts/distill_contributor_skill.py \
  --repo https://github.com/facebook/react \
  --contributor "Dan Abramov" \
  --commit abc1234 \
  --username gaearon \
  --out ./distilled
```

**Generate evidence files for manual refinement:**
```bash
python scripts/distill_contributor_skill.py \
  --repo /path/to/repo \
  --contributor "Jane Zhang" \
  --username janezhang \
  --out ./distilled \
  --write-evidence
```

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

## Project structure

```
github-contributor-distiller/
├── SKILL.md                              # Skill definition and workflow
├── agents/
│   └── openai.yaml                       # OpenAI agent interface config
├── references/
│   ├── analysis-rubric.md                # Evidence collection rubric
│   └── distilled-skill-template.md       # Output template
└── scripts/
    └── distill_contributor_skill.py      # Main distillation script
```

## How identity resolution works

The tool scans `author.name`, `author.email`, `committer.name`, and `committer.email` across the entire git history. It uses a scoring system:

- Exact email match: 100
- Exact name match: 95
- Exact username (email local-part) match: 92
- Compact name match (case/space insensitive): 90
- Substring matches: 66-78

When ambiguous, the tool outputs a candidate table and exits — it never guesses.

## Confidence levels

| Commits | Confidence | Meaning |
|---:|---|---|
| < 5 | **Low** | Treat all conclusions as tentative |
| 5-19 | **Medium** | Patterns may be concentrated in one area |
| 20+ | **High** | Reliable cross-area patterns |

## Integration with AI agents

The generated `SKILL.md` is designed to be consumed as a skill file by AI coding agents (Claude, ChatGPT, etc.). The YAML frontmatter (`name` + `description`) enables automatic skill discovery, and the structured sections provide concrete, actionable guidance rather than vague personality traits.

## Requirements

- Python 3.8+
- `git` available on PATH
- For GitHub URLs: network access (public repos) or configured git credentials (private repos)

No external Python packages required — uses only the standard library.

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
