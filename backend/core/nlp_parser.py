# backend/core/nlp_parser.py
import re
from typing import Dict, Any

class Parsed:
    def __init__(self, intent: str, slots: Dict[str, Any]):
        self.intent = intent
        self.slots = slots

class NLPParser:

    @staticmethod
    def parse(text: str) -> Parsed:
        t = (text or "").strip()
        low = t.lower()

        # 1) Simple "add" patterns
        m = re.search(r"(?:add|create)\s+(?:a\s+)?task\s+(?:to\s+)?(.*)", low)
        if m and m.group(1).strip():
            return Parsed("add_task", {"title": m.group(1).strip()})

        # Also accept "add <title>" (short form)
        if low.startswith("add "):
            cleaned = low[4:].strip()
            if cleaned:
                return Parsed("add_task", {"title": cleaned})

        # 2) Complete / done
        m = re.search(r"(?:complete|finish|done)\s+(.*)", low)
        if m and m.group(1).strip():
            return Parsed("complete_task", {"query": m.group(1).strip()})

        # 3) Delete
        m = re.search(r"(?:delete|remove)\s+(.*)", low)
        if m and m.group(1).strip():
            return Parsed("delete_task", {"query": m.group(1).strip()})

        # 4) Show / list
        if "show tasks" in low or low.strip() == "tasks" or "list tasks" in low:
            return Parsed("list_tasks", {})

        # 5) Memory simple
        if low.startswith("memory") or low.startswith("fetch memory") or low.startswith("show memory"):
            return Parsed("memory_fetch", {"raw": t})

        # 6) Memory update basic
        m = re.search(r"(?:update|set|change)\s+([^\s]+)\s*(?:to|=)\s*(.*)", low)
        if m:
            return Parsed("memory_update", {"key": m.group(1).strip(), "value": m.group(2).strip()})

        # 7) PDF quick
        if "pdf" in low:
            return Parsed("generate_pdf", {"raw": t})

        # 8) Search
        if low.startswith("search ") or low.startswith("find "):
            return Parsed("search", {"raw": t})

        # 9) Short-sentence fallback -> treat as add task
        words = low.split()
        if 1 <= len(words) <= 6 and len(low) < 120:
            if not low.endswith("?") and not re.search(r"\b(what|who|how|why|when)\b", low):
                return Parsed("add_task", {"title": t})

        # 10) fallback
        return Parsed("fallback", {"raw": t})
