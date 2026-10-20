from pathlib import Path

import pytest

from trace_research.explorer import inspect_repository


def test_finds_matching_python_file_and_extracts_symbols(tmp_path: Path):
    (tmp_path / "repair.py").write_text(
        "import ast\n\ndef verify_patch():\n    return True\n",
        encoding="utf-8",
    )
    (tmp_path / "unrelated.txt").write_text("ignored extension", encoding="utf-8")
    results = inspect_repository(tmp_path, "verify patch", limit=5)
    assert results
    assert results[0].path == "repair.py"
    assert "verify_patch" in results[0].symbols
    assert "ast" in results[0].imports


def test_ignores_virtual_environment(tmp_path: Path):
    ignored = tmp_path / ".venv" / "lib"
    ignored.mkdir(parents=True)
    (ignored / "agent.py").write_text("def repair_bug(): pass", encoding="utf-8")
    (tmp_path / "src.py").write_text("def other(): pass", encoding="utf-8")
    results = inspect_repository(tmp_path, "repair bug")
    assert all(".venv" not in result.path for result in results)


def test_requires_nonempty_query(tmp_path: Path):
    with pytest.raises(ValueError):
        inspect_repository(tmp_path, "!!!")


def test_requires_existing_directory(tmp_path: Path):
    with pytest.raises(NotADirectoryError):
        inspect_repository(tmp_path / "missing", "bug fix")


def test_limit_must_be_positive(tmp_path: Path):
    with pytest.raises(ValueError):
        inspect_repository(tmp_path, "bug fix", limit=0)
