# report.py
from __future__ import annotations
import json
from html import escape
from pathlib import Path
from typing import Dict


def write_json(result: Dict, path: str = "output/report.json") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return p


def write_html(result: Dict, path: str = "output/report.html") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    def color(status: str) -> str:
        return {
            "passed": "#1b8a3e",
            "failed": "#c62828",
            "skipped": "#9e9e9e",
        }.get(status, "#333")

    parts = [
        "<html><head><meta charset='utf-8'><title>Gherkin Report</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;background:#fafafa;}",
        ".card{border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0;background:#fff;}",
        ".step{padding:6px 0;border-bottom:1px dashed #eee;font-family:Menlo,monospace;font-size:13px;}",
        ".meta{font-size:13px;color:#666;margin-bottom:8px;}",
        "code{background:#f5f5f5;padding:2px 4px;border-radius:4px;}",
        ".badge{display:inline-block;padding:2px 6px;border-radius:4px;font-size:12px;margin-right:4px;background:#eee;}",
        "</style></head><body>",
        f"<h1>Feature: {escape(result.get('feature',''))}</h1>",
        f"<p>Status: <strong style='color:{color(result['status'])}'>{escape(result['status'])}</strong></p>",
    ]

    for scenario in result["scenarios"]:
        src = scenario.get("source") or {}
        rule = scenario.get("rule")
        kind = src.get("kind") or "scenario"

        meta_bits = []
        if rule:
            meta_bits.append(f"Rule: {escape(rule)}")
        meta_bits.append(f"Type: {escape(kind)}")
        if kind == "outline":
            ex_name = src.get("examples_name") or ""
            row_idx = src.get("row_index")
            if ex_name:
                meta_bits.append(f"Examples: {escape(ex_name)}")
            if row_idx is not None:
                meta_bits.append(f"Row: {row_idx}")

        parts.append("<div class='card'>")
        parts.append(
            f"<h2>Scenario: {escape(scenario['name'])}</h2>"
        )
        parts.append(
            f"<p>Status: <strong style='color:{color(scenario['status'])}'>{escape(scenario['status'])}</strong></p>"
        )
        if meta_bits:
            parts.append(f"<p class='meta'>{' · '.join(meta_bits)}</p>")

        for step in scenario["steps"]:
            err_html = ""
            if step.get("error"):
                err_html = f"<pre>{escape(step['error'])}</pre>"
            parts.append(
                "<div class='step'>"
                f"<span class='badge'>{escape(step['keyword'])}</span>"
                f"{escape(step['text'])} - "
                f"<strong style='color:{color(step['status'])}'>{escape(step['status'])}</strong>"
                f"{err_html}</div>"
            )

        parts.append("</div>")

    parts.append("</body></html>")
    p.write_text("".join(parts), encoding="utf-8")
    return p