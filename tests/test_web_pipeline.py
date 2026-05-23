"""Tests for web pipeline helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.web.pipeline import create_template_bytes, run_pipeline


def test_create_template_bytes(tmp_path):
    data = create_template_bytes("both", include_sample=True)
    assert data[:2] == b"PK"
    out = tmp_path / "t.xlsx"
    out.write_bytes(data)
    result = run_pipeline(out, descriptivos=True, cb=True, pls=False, bootstraps=100, processes=1)
    assert any(log.step == "descriptivos" for log in result.logs)
