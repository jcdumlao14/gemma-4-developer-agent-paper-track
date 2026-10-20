from pathlib import Path

import pytest

from trace_research.bm25 import rank_repository_bm25


def test_bm25_finds_relevant_document(tmp_path: Path):
    (tmp_path / "repair.py").write_text(
        "def verify_patch():\n    return True\n",
        encoding="utf-8",
    )
    (tmp_path / "garden.py").write_text(
        "flowers grow in a garden",
        encoding="utf-8",
    )
    results = rank_repository_bm25(
        tmp_path,
        "verify patch",
        limit=5,
    )
    assert results
    assert results[0][0] == "repair.py"
    assert results[0][1] > 0


def test_bm25_honors_path_exclusions(tmp_path: Path):
    (tmp_path / "target.py").write_text(
        "repository evidence retrieval",
        encoding="utf-8",
    )
    hidden = tmp_path / "labels" / "case.json"
    hidden.parent.mkdir()
    hidden.write_text(
        '{"query": "repository evidence retrieval"}',
        encoding="utf-8",
    )
    results = rank_repository_bm25(
        tmp_path,
        "repository evidence retrieval",
        exclude_paths=["labels"],
    )
    assert all(not path.startswith("labels/") for path, _ in results)


def test_bm25_validates_parameters(tmp_path: Path):
    with pytest.raises(ValueError):
        rank_repository_bm25(tmp_path, "valid query", limit=0)
    with pytest.raises(ValueError):
        rank_repository_bm25(tmp_path, "valid query", b=1.5)
    with pytest.raises(ValueError):
        rank_repository_bm25(tmp_path, "!!!")
