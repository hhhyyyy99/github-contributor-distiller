#!/usr/bin/env python3
"""
Distill a repository contributor's observable commit history into [username]/SKILL.md.

The script works with a local git repository path or a cloneable GitHub URL. It scans
commit author/committer identities, resolves the requested contributor, summarizes
matching commits, and renders a bounded contributor skill draft.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

FIELD_SEP = "\x1f"

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript/react",
    ".ts": "typescript",
    ".tsx": "typescript/react",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".c": "c",
    ".h": "c/cpp header",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".hpp": "cpp header",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".ps1": "powershell",
    ".sql": "sql",
    ".md": "markdown/docs",
    ".rst": "docs",
    ".json": "json config/data",
    ".yaml": "yaml config",
    ".yml": "yaml config",
    ".toml": "toml config",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".proto": "protobuf",
    ".tf": "terraform",
    ".dockerfile": "docker",
}

CONVENTIONAL_RE = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([^)]+\))?(!)?:",
    re.IGNORECASE,
)


def run(cmd: Sequence[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        joined = " ".join(cmd)
        raise RuntimeError(f"command failed ({proc.returncode}): {joined}\n{proc.stderr.strip()}")
    return proc


def git(repo: Path, args: Sequence[str], check: bool = True) -> str:
    return run(["git", "-C", str(repo), *args], check=check).stdout


def norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm_text(value))


def email_local(email: str) -> str:
    return norm_text(email).split("@", 1)[0]


def slugify(value: str, default: str = "contributor") -> str:
    value = norm_text(value)
    value = value.replace("@", "-")
    slug = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return (slug or default)[:64].strip("-") or default


def repo_name_from_url_or_path(repo_input: str) -> str:
    clean = repo_input.rstrip("/")
    clean = clean[:-4] if clean.endswith(".git") else clean
    name = clean.rsplit("/", 1)[-1]
    return slugify(name, "repository")


def prepare_repo(repo_input: str, branch: Optional[str]) -> Tuple[Path, Optional[Path], str]:
    expanded = Path(os.path.expanduser(repo_input))
    if expanded.exists():
        root = git(expanded, ["rev-parse", "--show-toplevel"]).strip()
        repo = Path(root)
        label = repo_name_from_url_or_path(str(repo))
        return repo, None, label

    temp_root = Path(tempfile.mkdtemp(prefix="contributor-distiller-"))
    clone_dir = temp_root / repo_name_from_url_or_path(repo_input)
    cmd = ["git", "clone", "--quiet"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([repo_input, str(clone_dir)])
    run(cmd)
    return clone_dir, temp_root, repo_name_from_url_or_path(repo_input)


def log_base_args(branch: Optional[str], since: Optional[str], until: Optional[str]) -> List[str]:
    args = ["log"]
    if branch:
        args.append(branch)
    else:
        args.append("--all")
    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")
    return args


def scan_identities(repo: Path, branch: Optional[str], since: Optional[str], until: Optional[str]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    args = log_base_args(branch, since, until) + [f"--format=%aN{FIELD_SEP}%aE{FIELD_SEP}%cN{FIELD_SEP}%cE"]
    output = git(repo, args)
    identities: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for line in output.splitlines():
        parts = line.split(FIELD_SEP)
        if len(parts) != 4:
            continue
        author_name, author_email, committer_name, committer_email = parts
        for role, name, email in (
            ("author", author_name, author_email),
            ("committer", committer_name, committer_email),
        ):
            key = (name.strip(), email.strip())
            if not key[0] and not key[1]:
                continue
            item = identities.setdefault(
                key,
                {"name": key[0], "email": key[1], "author_commits": 0, "committer_commits": 0},
            )
            item[f"{role}_commits"] += 1
    return identities


def identity_score(query: str, identity: Dict[str, Any]) -> int:
    q_norm = norm_text(query)
    q_compact = compact(query)
    if not q_norm:
        return 0
    name = identity.get("name", "")
    email = identity.get("email", "")
    n_norm = norm_text(name)
    e_norm = norm_text(email)
    local = email_local(email)
    n_compact = compact(name)
    local_compact = compact(local)

    if q_norm == e_norm:
        return 100
    if q_norm == n_norm:
        return 95
    if q_norm == local:
        return 92
    if q_compact and q_compact == n_compact:
        return 90
    if q_compact and q_compact == local_compact:
        return 88
    if q_norm in e_norm:
        return 78
    if q_norm in n_norm:
        return 72
    if q_compact and q_compact in n_compact:
        return 68
    if q_compact and q_compact in local_compact:
        return 66
    return 0


def candidate_rows(scored: List[Tuple[int, Dict[str, Any]]], limit: int = 20) -> List[Dict[str, Any]]:
    rows = []
    for score, item in scored[:limit]:
        rows.append(
            {
                "score": score,
                "name": item["name"],
                "email": item["email"],
                "author_commits": item["author_commits"],
                "committer_commits": item["committer_commits"],
            }
        )
    return rows


def resolve_identities(
    identities: Dict[Tuple[str, str], Dict[str, Any]],
    contributor: str,
    emails: Sequence[str],
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_items = list(identities.values())
    if emails:
        wanted = {norm_text(e) for e in emails}
        matched = [item for item in all_items if norm_text(item.get("email", "")) in wanted]
        scored = [(100, item) for item in matched]
        if matched:
            return "resolved", matched, candidate_rows(scored)
        fallback = sorted(((identity_score(contributor, item), item) for item in all_items), key=lambda pair: pair[0], reverse=True)
        return "not_found", [], candidate_rows(fallback)

    scored = sorted(
        ((identity_score(contributor, item), item) for item in all_items),
        key=lambda pair: (pair[0], item_commit_count(pair[1])),
        reverse=True,
    )
    scored = [(score, item) for score, item in scored if score > 0]
    if not scored:
        fallback = sorted(((0, item) for item in all_items), key=lambda pair: item_commit_count(pair[1]), reverse=True)
        return "not_found", [], candidate_rows(fallback)

    q_norm = norm_text(contributor)
    q_compact = compact(contributor)
    exact_name = [item for score, item in scored if norm_text(item["name"]) == q_norm or compact(item["name"]) == q_compact]
    if exact_name:
        return "resolved", exact_name, candidate_rows(scored)

    exact_local = [item for score, item in scored if email_local(item["email"]) == q_norm or compact(email_local(item["email"])) == q_compact]
    if len(exact_local) == 1:
        return "resolved", exact_local, candidate_rows(scored)
    if len(exact_local) > 1 and len({norm_text(item["name"]) for item in exact_local}) == 1:
        return "resolved", exact_local, candidate_rows(scored)

    top_score = scored[0][0]
    top = [item for score, item in scored if score == top_score]
    top_names = {norm_text(item["name"]) for item in top}
    if top_score >= 85 and len(top_names) == 1:
        return "resolved", top, candidate_rows(scored)
    if top_score >= 85 and len(top) == 1:
        return "resolved", top, candidate_rows(scored)

    loose = [item for score, item in scored if score >= 60]
    loose_names = {norm_text(item["name"]) for item in loose}
    if len(loose) == 1:
        return "resolved", loose, candidate_rows(scored)
    if len(loose_names) == 1 and loose:
        return "resolved", loose, candidate_rows(scored)

    return "ambiguous", [], candidate_rows(scored)


def item_commit_count(item: Dict[str, Any]) -> int:
    return int(item.get("author_commits", 0)) + int(item.get("committer_commits", 0))



def identities_from_commits(repo: Path, commit_hashes: Sequence[str], role: str) -> List[Dict[str, Any]]:
    resolved: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for commit_hash in commit_hashes:
        output = git(repo, ["show", "-s", f"--format=%aN{FIELD_SEP}%aE{FIELD_SEP}%cN{FIELD_SEP}%cE", commit_hash])
        parts = output.strip().split(FIELD_SEP)
        if len(parts) != 4:
            continue
        author_name, author_email, committer_name, committer_email = parts
        selected: List[Tuple[str, str, str]] = []
        if role in {"author", "both"}:
            selected.append(("author", author_name, author_email))
        if role in {"committer", "both"}:
            selected.append(("committer", committer_name, committer_email))
        for selected_role, name, email in selected:
            key = (name.strip(), email.strip())
            if not key[0] and not key[1]:
                continue
            item = resolved.setdefault(
                key,
                {"name": key[0], "email": key[1], "author_commits": 0, "committer_commits": 0},
            )
            item[f"{selected_role}_commits"] += 1
    return list(resolved.values())

def collect_commits(
    repo: Path,
    branch: Optional[str],
    since: Optional[str],
    until: Optional[str],
    identities: Sequence[Dict[str, Any]],
    max_commits: int,
) -> List[Dict[str, Any]]:
    identity_keys = {(norm_text(item["name"]), norm_text(item["email"])) for item in identities}
    args = log_base_args(branch, since, until) + [
        f"--format=%H{FIELD_SEP}%aN{FIELD_SEP}%aE{FIELD_SEP}%cN{FIELD_SEP}%cE{FIELD_SEP}%ad{FIELD_SEP}%s",
        "--date=short",
    ]
    output = git(repo, args)
    commits: List[Dict[str, Any]] = []
    seen = set()
    for line in output.splitlines():
        parts = line.split(FIELD_SEP)
        if len(parts) < 7:
            continue
        commit_hash, author_name, author_email, committer_name, committer_email, date, subject = parts[:7]
        author_key = (norm_text(author_name), norm_text(author_email))
        committer_key = (norm_text(committer_name), norm_text(committer_email))
        if author_key not in identity_keys and committer_key not in identity_keys:
            continue
        if commit_hash in seen:
            continue
        seen.add(commit_hash)
        commits.append(
            {
                "hash": commit_hash,
                "short_hash": commit_hash[:12],
                "author_name": author_name,
                "author_email": author_email,
                "committer_name": committer_name,
                "committer_email": committer_email,
                "date": date,
                "subject": subject,
            }
        )
        if len(commits) >= max_commits:
            break
    return commits


def parse_numstat(repo: Path, commit_hash: str) -> Tuple[List[Dict[str, Any]], int, int]:
    output = git(repo, ["show", "--numstat", "--format=", "--find-renames", commit_hash])
    files: List[Dict[str, Any]] = []
    total_add = 0
    total_del = 0
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_raw, del_raw, path = parts[0], parts[1], "\t".join(parts[2:])
        additions = int(add_raw) if add_raw.isdigit() else 0
        deletions = int(del_raw) if del_raw.isdigit() else 0
        total_add += additions
        total_del += deletions
        files.append(
            {
                "path": path,
                "additions": additions,
                "deletions": deletions,
                "extension": path_extension(path),
                "top_dir": top_dir(path),
                "role": classify_path(path),
            }
        )
    return files, total_add, total_del


def path_extension(path: str) -> str:
    lower = path.lower()
    if lower.endswith("dockerfile") or "/dockerfile" in lower:
        return ".dockerfile"
    suffix = Path(path).suffix.lower()
    return suffix or "[no extension]"


def top_dir(path: str) -> str:
    clean = path.strip()
    if not clean or "/" not in clean:
        return "(repo root)"
    return clean.split("/", 1)[0]


def classify_path(path: str) -> str:
    lower = path.lower()
    base = Path(path).name.lower()
    if re.search(r"(^|/)(test|tests|spec|specs|__tests__)(/|$)", lower) or re.search(r"(test|spec)\.[a-z0-9]+$", base):
        return "test"
    if lower.endswith(('.md', '.rst', '.adoc')) or re.search(r"(^|/)(docs?|documentation)(/|$)", lower):
        return "docs"
    if re.search(r"(^|/)(ci|\.github|\.circleci|\.gitlab)(/|$)", lower):
        return "ci"
    if re.search(r"(^|/)(migrations?|db/migrate)(/|$)", lower):
        return "migration"
    if base in {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "pyproject.toml", "requirements.txt", "pom.xml", "build.gradle", "settings.gradle", "makefile", "dockerfile"}:
        return "config/build"
    if lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env.example')):
        return "config"
    return "source"


def summarize_commits(repo: Path, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    path_counter: collections.Counter[str] = collections.Counter()
    dir_counter: collections.Counter[str] = collections.Counter()
    ext_counter: collections.Counter[str] = collections.Counter()
    role_counter: collections.Counter[str] = collections.Counter()
    language_counter: collections.Counter[str] = collections.Counter()
    changed_files_counts: List[int] = []
    additions_counts: List[int] = []
    deletions_counts: List[int] = []
    enriched_commits: List[Dict[str, Any]] = []
    conventional_count = 0
    conventional_types: collections.Counter[str] = collections.Counter()
    scope_counter: collections.Counter[str] = collections.Counter()

    for commit in commits:
        files, additions, deletions = parse_numstat(repo, commit["hash"])
        commit = dict(commit)
        commit["files"] = files
        commit["additions"] = additions
        commit["deletions"] = deletions
        commit["file_count"] = len(files)
        enriched_commits.append(commit)
        changed_files_counts.append(len(files))
        additions_counts.append(additions)
        deletions_counts.append(deletions)
        for f in files:
            path_counter[f["path"]] += 1
            dir_counter[f["top_dir"]] += 1
            ext_counter[f["extension"]] += 1
            role_counter[f["role"]] += 1
            language_counter[LANGUAGE_BY_EXTENSION.get(f["extension"], f["extension"])] += 1
        match = CONVENTIONAL_RE.match(commit["subject"] or "")
        if match:
            conventional_count += 1
            conventional_types[match.group(1).lower()] += 1
            if match.group(2):
                scope_counter[match.group(2).strip("() ")] += 1

    dates = [c["date"] for c in enriched_commits if c.get("date")]
    commit_count = len(enriched_commits)
    test_commits = sum(1 for c in enriched_commits if any(f["role"] == "test" for f in c["files"]))
    docs_commits = sum(1 for c in enriched_commits if any(f["role"] == "docs" for f in c["files"]))
    config_commits = sum(1 for c in enriched_commits if any(f["role"] in {"config", "config/build", "ci"} for f in c["files"]))

    return {
        "commit_count": commit_count,
        "first_date": min(dates) if dates else None,
        "last_date": max(dates) if dates else None,
        "confidence": confidence_label(commit_count, len(dir_counter)),
        "top_paths": path_counter.most_common(15),
        "top_directories": dir_counter.most_common(12),
        "top_extensions": ext_counter.most_common(12),
        "top_languages": language_counter.most_common(8),
        "role_counts": role_counter.most_common(),
        "avg_files_changed": safe_mean(changed_files_counts),
        "median_files_changed": safe_median(changed_files_counts),
        "avg_additions": safe_mean(additions_counts),
        "avg_deletions": safe_mean(deletions_counts),
        "test_commit_count": test_commits,
        "docs_commit_count": docs_commits,
        "config_commit_count": config_commits,
        "conventional_commit_count": conventional_count,
        "conventional_types": conventional_types.most_common(),
        "conventional_scopes": scope_counter.most_common(10),
        "subjects": [c["subject"] for c in enriched_commits[:20]],
        "commits": enriched_commits,
    }


def safe_mean(values: Sequence[int]) -> float:
    return round(statistics.mean(values), 1) if values else 0.0


def safe_median(values: Sequence[int]) -> float:
    return round(float(statistics.median(values)), 1) if values else 0.0


def confidence_label(commit_count: int, distinct_dirs: int) -> str:
    if commit_count < 5:
        return "low"
    if commit_count < 20 or distinct_dirs <= 1:
        return "medium"
    return "high"


def pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "0%"
    return f"{round(part * 100 / whole)}%"


def bullets(items: Iterable[str], fallback: str = "- No stable signal found in the sampled commits.") -> str:
    rows = [f"- {item}" for item in items if item]
    return "\n".join(rows) if rows else fallback


def fmt_counter(items: Sequence[Tuple[str, int]], limit: int = 8) -> str:
    if not items:
        return "no stable signal"
    return ", ".join(f"`{key}` ({count})" for key, count in items[:limit])


def derive_working_style(summary: Dict[str, Any]) -> List[str]:
    n = summary["commit_count"]
    items = []
    avg_files = summary["avg_files_changed"]
    median_files = summary["median_files_changed"]
    if n:
        if median_files <= 2:
            items.append(f"Prefer localized changes; the median sampled commit changes {median_files:g} files.")
        elif median_files <= 6:
            items.append(f"Use moderately scoped commits; the median sampled commit changes {median_files:g} files.")
        else:
            items.append(f"Expect broader cross-file work; the median sampled commit changes {median_files:g} files.")
        items.append(f"Typical sampled change size is about {avg_files:g} files, {summary['avg_additions']:g} additions, and {summary['avg_deletions']:g} deletions per commit.")
        if summary["test_commit_count"]:
            items.append(f"Tests are part of the pattern in {summary['test_commit_count']} of {n} commits ({pct(summary['test_commit_count'], n)}). Update or add nearby tests when behavior changes.")
        else:
            items.append("No test-file touch was detected in the sampled commits; still run or add tests when the requested change affects behavior.")
        if summary["docs_commit_count"]:
            items.append(f"Documentation is touched in {summary['docs_commit_count']} of {n} commits ({pct(summary['docs_commit_count'], n)}), so update docs when user-visible behavior changes.")
        if summary["config_commit_count"]:
            items.append(f"Configuration, build, or CI files appear in {summary['config_commit_count']} commits ({pct(summary['config_commit_count'], n)}); preserve existing config style and avoid unrelated churn.")
        if summary["conventional_commit_count"]:
            items.append(f"Commit subjects use conventional-commit-like prefixes in {summary['conventional_commit_count']} of {n} commits ({pct(summary['conventional_commit_count'], n)}). Common types: {fmt_counter(summary['conventional_types'], 6)}.")
        else:
            items.append("Commit subjects do not show a strong conventional-commit prefix pattern in the sample; mirror the repository's nearby commit style when asked to draft messages.")
    return items


def derive_implementation_rules(summary: Dict[str, Any]) -> List[str]:
    rules = []
    if summary["top_directories"]:
        rules.append(f"Start by inspecting the dominant touched areas: {fmt_counter(summary['top_directories'], 6)}.")
    if summary["top_languages"]:
        rules.append(f"Use idioms consistent with the main observed file types/languages: {fmt_counter(summary['top_languages'], 6)}.")
    role_names = {role for role, _ in summary["role_counts"]}
    if "test" in role_names:
        rules.append("When changing behavior, look for adjacent test files or mirrored test directories and update them in the same change.")
    if "docs" in role_names:
        rules.append("When changing public behavior, CLI behavior, configuration, or developer workflow, check whether docs should change with the code.")
    if "config/build" in role_names or "config" in role_names or "ci" in role_names:
        rules.append("For config/build/CI edits, keep diffs minimal and preserve existing ordering, formatting, and comments.")
    rules.extend(
        [
            "Prefer existing repository abstractions over introducing new cross-cutting patterns.",
            "Keep unrelated refactors out of the change unless the user explicitly asks for them.",
            "Match local naming, imports, error handling, logging, and formatting in the files being edited.",
            "If the evidence is thin for a module, follow the surrounding code and repository docs rather than forcing this contributor profile.",
        ]
    )
    return rules


def render_skill_md(
    target_name: str,
    contributor: str,
    repo_label: str,
    repo_input: str,
    identities: Sequence[Dict[str, Any]],
    summary: Dict[str, Any],
) -> str:
    identity_lines = [f"{item['name']} <{item['email']}>".strip() for item in identities]
    desc = (
        f"repo-specific contributor guidance distilled from git commit history. use when working in {slugify(repo_label)} "
        f"and asked to implement, modify, review, or explain code in a style consistent with {slugify(contributor)}'s observed contributions."
    )
    n = summary["commit_count"]
    limitations = []
    if n < 5:
        limitations.append("The sample has fewer than 5 commits, so treat all style conclusions as low-confidence.")
    if not summary["commits"]:
        limitations.append("No matching commits were collected; rerun identity resolution with a more specific name or email.")
    if summary["confidence"] != "high":
        limitations.append("Prefer current repository instructions and local file conventions over this profile when they conflict.")
    if not limitations:
        limitations.append("The profile is evidence-based but should not override current project instructions, tests, or explicit user requests.")

    sample_subjects = summary["subjects"][:10]
    sample_subject_text = "\n".join(f"- {subject}" for subject in sample_subjects) if sample_subjects else "- No commit subjects were available."

    content = f"""---
name: {target_name}
description: {desc}
---

# {contributor} contributor skill for {repo_label}

## Overview

Use this skill when working in `{repo_label}` and the user wants implementation, review, debugging, or explanation to align with `{contributor}`'s observed contribution style in this repository.

This is a repository-facing style guide, not a biography. It summarizes observable commit behavior only.

## Scope and evidence

- Repository input: `{repo_input}`
- Repository label: `{repo_label}`
- Contributor query: `{contributor}`
- Resolved identities: {', '.join(identity_lines) if identity_lines else 'none'}
- Commit sample: {n} commits from {summary['first_date'] or 'unknown'} to {summary['last_date'] or 'unknown'}
- Confidence: {summary['confidence']}
- Limitations: {' '.join(limitations)}

## How to use this skill

Apply this skill after reading the user's request, current repository instructions, project docs, and relevant source files. Use it to bias decisions about change scope, file placement, tests, and review habits. Do not use it to override explicit user instructions or current code conventions.

## Repository orientation

- Most touched directories: {fmt_counter(summary['top_directories'], 8)}
- Most touched file types/languages: {fmt_counter(summary['top_languages'], 8)}
- Most repeated paths: {fmt_counter(summary['top_paths'], 8)}
- Change roles observed: {fmt_counter(summary['role_counts'], 8)}

Before editing, inspect nearby files in these areas and follow their current patterns.

## Contributor working style

{bullets(derive_working_style(summary))}

Representative sampled commit subjects:

{sample_subject_text}

## Implementation rules

{bullets(derive_implementation_rules(summary))}

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
- Any commit message or summary mirrors the repository's recent style and avoids overstating the change.

## Guardrails

- Do not infer personal traits, intent, availability, seniority, or private preferences from commit history.
- Do not copy large historical code excerpts into responses.
- Treat this profile as a set of tendencies, not absolute rules.
- When evidence is sparse or conflicting, say so and prioritize the current codebase.
"""
    return content


def write_candidates(out_dir: Path, target_name: str, contributor: str, candidates: Sequence[Dict[str, Any]], status: str) -> Path:
    target_dir = out_dir / target_name
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / "identity-candidates.md"
    rows = [f"# Identity resolution {status} for {contributor}", ""]
    rows.append("The contributor query did not resolve to one clear identity. Ask the user to choose an email/name or rerun with `--email`.")
    rows.append("")
    rows.append("| score | name | email | author commits | committer commits |")
    rows.append("|---:|---|---|---:|---:|")
    for item in candidates:
        rows.append(
            f"| {item['score']} | {item['name']} | {item['email']} | {item['author_commits']} | {item['committer_commits']} |"
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def write_diff_samples(repo: Path, commits: Sequence[Dict[str, Any]], out_path: Path, max_bytes: int) -> None:
    chunks = ["# Bounded diff samples", "", "Use these internally to refine style. Do not paste large excerpts into the final SKILL.md.", ""]
    total = len("\n".join(chunks).encode("utf-8"))
    for commit in commits[:12]:
        header = f"\n## {commit['short_hash']} - {commit['subject']}\n\n"
        diff = git(repo, ["show", "--format=fuller", "--stat", "--patch", "--find-renames", "--unified=40", commit["hash"]], check=False)
        piece = header + diff
        encoded_len = len(piece.encode("utf-8", errors="replace"))
        if total + encoded_len > max_bytes:
            remaining = max_bytes - total
            if remaining <= 0:
                break
            piece = piece.encode("utf-8", errors="replace")[:remaining].decode("utf-8", errors="replace")
            chunks.append(piece)
            break
        chunks.append(piece)
        total += encoded_len
    out_path.write_text("\n".join(chunks), encoding="utf-8")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Distill a git contributor into [username]/SKILL.md")
    parser.add_argument("--repo", required=True, help="GitHub URL or local git repository path")
    parser.add_argument("--contributor", required=True, help="Contributor name, username, or email to resolve in git history")
    parser.add_argument("--username", help="Output directory slug; defaults to sanitized contributor query")
    parser.add_argument("--email", action="append", default=[], help="Exact contributor email to disambiguate identity; repeatable")
    parser.add_argument("--commit", action="append", default=[], help="Commit hash whose author identity should anchor contributor resolution; repeatable")
    parser.add_argument("--commit-identity-role", choices=["author", "committer", "both"], default="author", help="Which identity to take from --commit anchors")
    parser.add_argument("--branch", help="Branch or revision to scan; defaults to --all")
    parser.add_argument("--since", help="Only inspect commits after this date, passed to git log --since")
    parser.add_argument("--until", help="Only inspect commits before this date, passed to git log --until")
    parser.add_argument("--max-commits", type=int, default=80, help="Maximum matching commits to analyze")
    parser.add_argument("--max-diff-bytes", type=int, default=160000, help="Maximum bytes for optional diff_samples.md")
    parser.add_argument("--out", default=".", help="Output parent directory; writes [username]/SKILL.md inside it")
    parser.add_argument("--write-evidence", action="store_true", help="Also write analysis.json and diff_samples.md for internal refinement")
    parser.add_argument("--keep-clone", action="store_true", help="Keep temporary clone directory when repo is a URL")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    target_name = slugify(args.username or args.contributor)
    temp_root: Optional[Path] = None

    try:
        repo, temp_root, repo_label = prepare_repo(args.repo, args.branch)
        identities = scan_identities(repo, args.branch, args.since, args.until)
        if args.commit:
            anchors = identities_from_commits(repo, args.commit, args.commit_identity_role)
            anchor_names = {norm_text(item["name"]) for item in anchors if item.get("name")}
            anchor_emails = {norm_text(item["email"]) for item in anchors if item.get("email")}
            matched = [
                item
                for item in identities.values()
                if norm_text(item.get("email", "")) in anchor_emails
                or norm_text(item.get("name", "")) in anchor_names
            ] or anchors
            candidates = [
                {
                    "score": 100,
                    "name": item["name"],
                    "email": item["email"],
                    "author_commits": item.get("author_commits", 0),
                    "committer_commits": item.get("committer_commits", 0),
                }
                for item in matched
            ]
            status = "resolved" if matched else "not_found"
        else:
            status, matched, candidates = resolve_identities(identities, args.contributor, args.email)
        if status != "resolved":
            path = write_candidates(out_dir, target_name, args.contributor, candidates, status)
            print(f"identity resolution {status}; wrote candidates to {path}", file=sys.stderr)
            return 3 if status == "ambiguous" else 2

        commits = collect_commits(repo, args.branch, args.since, args.until, matched, args.max_commits)
        if not commits:
            path = write_candidates(out_dir, target_name, args.contributor, candidates, "not_found")
            print(f"no matching commits; wrote candidates to {path}", file=sys.stderr)
            return 2

        summary = summarize_commits(repo, commits)
        display_contributor = args.contributor
        if args.commit and matched and max(identity_score(args.contributor, item) for item in matched) == 0:
            display_contributor = matched[0].get("name") or args.contributor
        target_dir = out_dir / target_name
        target_dir.mkdir(parents=True, exist_ok=True)
        skill_md = render_skill_md(target_name, display_contributor, repo_label, args.repo, matched, summary)
        skill_path = target_dir / "SKILL.md"
        skill_path.write_text(skill_md, encoding="utf-8")

        if args.write_evidence:
            analysis = {
                "repo": args.repo,
                "repo_label": repo_label,
                "contributor": display_contributor,
                "contributor_query": args.contributor,
                "target_name": target_name,
                "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "matched_identities": matched,
                "identity_candidates": candidates,
                "summary": {k: v for k, v in summary.items() if k != "commits"},
                "commits": summary["commits"],
            }
            (target_dir / "analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
            write_diff_samples(repo, summary["commits"], target_dir / "diff_samples.md", args.max_diff_bytes)

        print(str(skill_path))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_root and not args.keep_clone:
            shutil.rmtree(temp_root, ignore_errors=True)
        elif temp_root:
            print(f"kept clone at {temp_root}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
