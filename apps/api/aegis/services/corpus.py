"""Corpus loader for scan targets."""

from __future__ import annotations

from pathlib import Path

TEXT_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".env.example",
    ".sh",
    ".html",
    ".css",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
    ".turbo",
}


def load_corpus(
    target: str | Path,
    max_bytes: int = 1_500_000,
    exclude_prefixes: list[str] | None = None,
) -> tuple[str, list[str]]:
    path = Path(target).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Target not found: {path}")

    files: list[str] = []
    chunks: list[str] = []
    total = 0
    excludes = [p.replace("\\", "/").rstrip("/") for p in (exclude_prefixes or [])]

    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text, [str(path)]

    for p in sorted(path.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            rel = str(p.relative_to(path)).replace("\\", "/")
        except ValueError:
            continue
        if excludes and any(
            rel == prefix or rel.startswith(prefix + "/") for prefix in excludes
        ):
            continue
        if p.suffix.lower() not in TEXT_EXTENSIONS and p.name not in {
            "Dockerfile",
            "Makefile",
            "LICENSE",
            "README",
        }:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files.append(rel)
        block = f"\n\n# FILE: {rel}\n{content}"
        if total + len(block) > max_bytes:
            remaining = max_bytes - total
            if remaining > 0:
                chunks.append(block[:remaining])
            break
        chunks.append(block)
        total += len(block)

    return "".join(chunks), files
