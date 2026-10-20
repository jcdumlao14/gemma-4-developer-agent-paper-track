from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_EXTENSIONS = {".py", ".md", ".toml", ".yaml", ".yml", ".json", ".kt", ".java", ".ts", ".tsx", ".js", ".jsx"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}


@dataclass(frozen=True)
class Evidence:
    path: str
    score: float
    matched_terms: tuple[str, ...]
    imports: tuple[str, ...]
    symbols: tuple[str, ...]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["matched_terms"] = list(self.matched_terms)
        result["imports"] = list(self.imports)
        result["symbols"] = list(self.symbols)
        return result


def _tokens(text: str) -> set[str]:
    """Extract identifiers and their underscore-separated components."""
    tokens: set[str] = set()
    for match in re.findall(r"[A-Za-z_][A-Za-z0-9_]{1,}", text):
        token = match.lower()
        tokens.add(token)
        tokens.update(part for part in token.split("_") if len(part) >= 2)
    return tokens


def _python_structure(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return (), ()
    imports: set[str] = set()
    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
    return tuple(sorted(imports)), tuple(sorted(symbols))


def inspect_repository(
    root: str | Path,
    query: str,
    *,
    limit: int = 10,
    extensions: Iterable[str] = DEFAULT_EXTENSIONS,
    exclude_paths: Iterable[str] = (),
) -> list[Evidence]:
    """Rank files using transparent lexical overlap plus light Python AST evidence.

    This is a deterministic baseline, not the full TRACE adaptive policy.
    It intentionally avoids reading ignored folders and large files.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    if limit < 1:
        raise ValueError("limit must be >= 1")

    query_terms = _tokens(query)
    if not query_terms:
        raise ValueError("query must contain at least one searchable term")

    allowed = set(extensions)
    excluded = {Path(item).as_posix().strip('/') for item in exclude_paths}
    candidates: list[Evidence] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        if any(
            rel_posix == item
            or rel_posix.startswith(item.rstrip('/') + '/')
            for item in excluded
        ):
            continue
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        path_terms = _tokens(str(rel))
        content_terms = _tokens(text)
        matched = query_terms & (path_terms | content_terms)
        if not matched:
            continue

        imports: tuple[str, ...] = ()
        symbols: tuple[str, ...] = ()
        if path.suffix.lower() == ".py":
            imports, symbols = _python_structure(text)

        # Explainable baseline: path matches receive more weight than content matches.
        path_matches = query_terms & path_terms
        content_matches = query_terms & content_terms
        score = (2.0 * len(path_matches)) + len(content_matches)
        candidates.append(Evidence(
            path=rel.as_posix(),
            score=score,
            matched_terms=tuple(sorted(matched)),
            imports=imports,
            symbols=symbols,
        ))

    return sorted(candidates, key=lambda e: (-e.score, e.path))[:limit]
