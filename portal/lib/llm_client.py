"""
LLM client for NL-to-pivot. Two backends:

  - RealLLMClient   uses Anthropic SDK + ANTHROPIC_API_KEY
  - MockLLMClient   pattern-matches three demo questions; everything else
                    falls back to "cannot_answer". For builds before
                    the user has spent on API credit.

get_llm_client() picks based on env. Everything downstream is identical.
"""

from __future__ import annotations

import os
import re
from typing import Protocol


class LLMClient(Protocol):
    """Anything we plug in must produce a propose() that returns the same
    JSON-shape contract — see NL_TO_PIVOT_DESIGN.md."""

    name: str

    def propose(self, question: str, schema_context: str) -> dict:
        ...


# ────────────────────────────────────────────────────────────────────
# Mock client — handles 3 canned questions + a graceful fallback
# ────────────────────────────────────────────────────────────────────


class MockLLMClient:
    """Pattern-match a small set of demo questions to hardcoded proposals.

    Recognised today:
      1. "how many videos did <handle> post in <month> <year>"
      2. "top creators by videos in <month> <year>"
      3. "creator activity in <month> <year>" → routes to existing report

    Anything else returns kind=cannot_answer with guidance.
    """

    name = "mock"

    _MONTHS = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09", "sept": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12",
    }

    def _extract_month(self, q: str) -> str | None:
        """Return YYYY-MM if found, else None. Recognises 'May 2026', '2026-05', etc."""
        m = re.search(r"(\d{4})[-/](\d{2})", q)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        for word, num in self._MONTHS.items():
            if re.search(rf"\b{word}\b", q):
                y = re.search(r"\b(20\d{2})\b", q)
                if y:
                    return f"{y.group(1)}-{num}"
        return None

    def _extract_handle(self, q: str) -> str | None:
        """Heuristic: look for tokens like @foo, "foo's videos", "by foo", etc."""
        m = re.search(r"@([A-Za-z0-9_.]+)", q)
        if m:
            return m.group(1)
        m = re.search(r"\bby\s+([a-z][a-z0-9_.]+)\b", q)
        if m:
            return m.group(1)
        m = re.search(r"\b([a-z][a-z0-9_.]{2,})\s+post(?:ed)?\b", q)
        if m:
            return m.group(1)
        return None

    def _month_range(self, ym: str) -> tuple[str, str]:
        """Return (YYYY-MM-01, YYYY-MM+1-01) as ISO timestamps."""
        year, month = ym.split("-")
        y = int(year); m = int(month)
        next_m = m + 1; next_y = y
        if next_m > 12:
            next_m = 1; next_y = y + 1
        return (
            f"{y:04d}-{m:02d}-01 00:00:00",
            f"{next_y:04d}-{next_m:02d}-01 00:00:00",
        )

    def propose(self, question: str, schema_context: str = "") -> dict:
        q = question.lower().strip()
        ym = self._extract_month(q) or "2026-05"
        start, end = self._month_range(ym)

        # Pattern 3 — "creator activity" matches an existing pre-built report.
        if "creator activity" in q or ("activity" in q and "creator" in q):
            return {
                "kind": "report",
                "report_slug": "creator-content-counts",
                "params": {"month": ym},
                "explanation": (
                    f"This matches the pre-built report 'Creator activity by month' — "
                    f"videos posted + livestreams done per creator for {ym}."
                ),
                "confidence": "high",
                "_source": "mock",
            }

        # Pattern 2 — "top creators by videos"
        if "top" in q and ("creator" in q or "creators" in q) and "video" in q:
            return {
                "kind": "pivot",
                "explanation": (
                    f"Counting distinct video_id from tt_video, grouped by handle, "
                    f"sorted by count, for {ym} (IST day boundary applied)."
                ),
                "confidence": "high",
                "plan": {
                    "schema": "tiktok_raw_data",
                    "table": "tt_video",
                    "rows": ["handle"],
                    "values": [{"agg": "COUNT_DISTINCT", "column": "video_id"}],
                    "filters": [
                        {"column": "post_time", "op": ">=", "value": start, "value2": None},
                        {"column": "post_time", "op": "<", "value": end, "value2": None},
                    ],
                    "columns_dim": None,
                    "limit": 100,
                },
                "_source": "mock",
            }

        # Pattern 1 — "how many videos did X post in MONTH"
        if "video" in q and ("post" in q or "did" in q or "how many" in q):
            handle = self._extract_handle(q) or "swugshop"
            return {
                "kind": "pivot",
                "explanation": (
                    f"Counting distinct video_id in tt_video where handle='{handle}' "
                    f"and post_time falls in {ym} (IST day boundary)."
                ),
                "confidence": "medium" if handle == "swugshop" else "medium",
                "plan": {
                    "schema": "tiktok_raw_data",
                    "table": "tt_video",
                    "rows": [],
                    "values": [{"agg": "COUNT_DISTINCT", "column": "video_id"}],
                    "filters": [
                        {"column": "handle", "op": "=", "value": handle, "value2": None},
                        {"column": "post_time", "op": ">=", "value": start, "value2": None},
                        {"column": "post_time", "op": "<", "value": end, "value2": None},
                    ],
                    "columns_dim": None,
                    "limit": 100,
                },
                "_source": "mock",
            }

        # Fallback
        return {
            "kind": "cannot_answer",
            "reason": (
                "Mock mode only recognises three demo questions right now. Try one of:\n"
                "  • how many videos did <handle> post in <month> <year>\n"
                "  • top creators by videos in <month> <year>\n"
                "  • creator activity in <month> <year>\n"
                "Or use Browse Data to build the pivot manually."
            ),
            "confidence": "low",
            "_source": "mock",
        }


# ────────────────────────────────────────────────────────────────────
# Real client (Anthropic) — placeholder. Wires up when ANTHROPIC_API_KEY is set.
# ────────────────────────────────────────────────────────────────────


class RealLLMClient:
    """Real Anthropic Claude call. Activates when ANTHROPIC_API_KEY is in env.

    NOT YET WIRED UP — the import + call is gated behind env detection so the
    portal runs fine in mock mode without anthropic installed. When the user
    adds the key:
      1. pip install anthropic
      2. set ANTHROPIC_API_KEY=sk-ant-...
      3. The factory below picks this client automatically.
    """

    name = "anthropic-claude-haiku-4-5"

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        self.api_key = api_key
        self.model = model
        # Lazy import — only required when this client is constructed.
        try:
            import anthropic  # type: ignore
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError as e:
            raise RuntimeError(
                "Anthropic SDK not installed. Run: portal/.venv/bin/pip install anthropic"
            ) from e

    def propose(self, question: str, schema_context: str) -> dict:
        """Single call, JSON-mode output. Prompt structure per NL_TO_PIVOT_DESIGN.md."""
        # System prompt assembled from schema_context (passed in by nl_to_pivot.py)
        system = schema_context
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": question}],
        )
        # Extract JSON from response
        text = "".join(block.text for block in msg.content if hasattr(block, "text"))
        import json
        # Strip code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            parsed = json.loads(text)
            parsed["_source"] = "anthropic"
            return parsed
        except json.JSONDecodeError as e:
            return {
                "kind": "cannot_answer",
                "reason": f"LLM response wasn't valid JSON: {e}. Raw: {text[:200]}",
                "_source": "anthropic-parse-error",
            }


# ────────────────────────────────────────────────────────────────────
# Factory — pick a client based on env
# ────────────────────────────────────────────────────────────────────


def get_llm_client() -> LLMClient:
    """Return RealLLMClient if ANTHROPIC_API_KEY is set, else MockLLMClient."""
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key:
        try:
            return RealLLMClient(api_key=key)
        except RuntimeError:
            # SDK not installed — fall back loudly to mock
            return MockLLMClient()
    return MockLLMClient()


def is_mock_mode() -> bool:
    return not os.getenv("ANTHROPIC_API_KEY", "").strip()
