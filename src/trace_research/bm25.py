from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from .explorer import DEFAULT_EXTENSIONS, IGNORED_DIRS


def _terms(text: str) -> list[str]:
    """Tokenize text while retaining term frequency."""
    result = []
    for match in re.findall(r"[A-Za-z_][A-Za-z0-9_]{1,}", text):
        token = match.lower()
        result.append(token)
        result.extend(part for part in token.split("_") if len(part) >= 2)
    return result


def rank_repository_bm25(
    root: str | Path,
    query: str,
    *,
    limit: int = 10,
    exclude_paths: Iterable[str] = (),
    extensions: Iterable[str] = DEFAULT_EXTENSIONS,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[tuple[str, float]]:
    """Rank repository files using BM25; return (relative_path, score).

    This is a retrieval baseline, not the full TRACE agent.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if k1 <= 0:
        raise ValueError("k1 must be > 0")
    if not 0 <= b <= 1:
        raise ValueError("b must be between 0 and 1")

    query_terms = _terms(query)
    if not query_terms:
        raise ValueError("query must contain at least one searchable term")

    excluded = {Path(item).as_posix().strip("/") for item in exclude_paths}
    allowed = {ext.lower() for ext in extensions}
    documents: list[tuple[str, list[str]]] = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        rel = path.relative_to(root)
        rel_text = rel.as_posix()
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if any(
            rel_text == item
            or rel_text.startswith(item.rstrip("/") + "/")
            for item in excluded
        ):
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        tokens = _terms(rel_text.replace("/", " ") + " " + content)
        if tokens:
            documents.append((rel_text, tokens))

    if not documents:
        return []

    document_count = len(documents)
    average_length = sum(len(tokens) for _, tokens in documents) / document_count
    query_counts = Counter(query_terms)
    document_frequency: Counter[str] = Counter()

    tokenized = []
    for rel_text, tokens in documents:
        frequencies = Counter(tokens)
        document_frequency.update(frequencies.keys())
        tokenized.append((rel_text, tokens, frequencies))

    scored = []
    for rel_text, tokens, frequencies in tokenized:
        score = 0.0
        doc_length = len(tokens)
        for term, query_frequency in query_counts.items():
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            df = document_frequency[term]
            inverse_document_frequency = math.log(
                1.0 + (document_count - df + 0.5) / (df + 0.5)
            )
            denominator = frequency + k1 * (
                1.0 - b + b * doc_length / average_length
            )
            term_score = (
                inverse_document_frequency
                * frequency * (k1 + 1.0)
                / denominator
            )
            score += query_frequency * term_score

        if score > 0:
            scored.append((rel_text, score))

    return sorted(scored, key=lambda item: (-item[1], item[0]))[:limit]
