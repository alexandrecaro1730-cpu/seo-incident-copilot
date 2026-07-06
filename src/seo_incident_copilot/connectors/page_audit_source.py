"""
Business objective:
Represent the kind of technical SEO audit data that would normally come from a
crawler, CMS, or custom page fetcher.

Coding objective:
Load page-audit JSON with explicit fields for indexability, canonicalization,
content depth, and page modules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_page_audit(data_dir: Path, relative_file: str) -> dict[str, Any]:
    """Load a page-audit fixture."""

    return json.loads((data_dir / relative_file).read_text(encoding="utf-8"))


def load_gsc_metrics(data_dir: Path, relative_file: str) -> dict[str, Any]:
    """Load simulated GSC trend data for the affected page/query."""

    return json.loads((data_dir / relative_file).read_text(encoding="utf-8"))
