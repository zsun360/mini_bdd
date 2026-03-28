import json
from html import escape
from pathlib import Path


def write_json(result, path="output/report.json"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def write_html(result, path="output/report.html"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    def color(status):
        return {
            "passed": "#1b8a3e",
            "failed": "#c62828",
            "skipped": "#9e9e9e"
        }.get(status, "#333")

    parts = [
        "<html><head><meta charset='utf-8'><title>Gherkin Report</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;}",
        ".card{border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0;}",
        ".step{padding:6px 0;border-bottom:1px dashed #eee;}",
        "code{background:#f5f5f5;padding:2px 4px;border-radius:4px;}",
        "</style></head><body>",
        f"<h1>Feature: {escape(result['feature'])}</h1>",
        f"<p>Status: <strong style='color:{color(result['status'])}'>{escape(result['status'])}</strong></p>"
    ]

    for scenario in result["scenarios"]:
        parts.append("<div class='card'>")
        parts.append(f"<h2>Scenario: {escape(scenario['name'])}</h2>")
        parts.append(f"<p>Status: <strong style='color:{color(scenario['status'])}'>{escape(scenario['status'])}</strong></p>")

        for step in scenario["steps"]:
            err = f"<pre>{escape(step.get('error', ''))}</pre>" if step.get("error") else ""
            parts.append(
                f"<div class='step'><code>{escape(step['keyword'])}</code> "
                f"{escape(step['text'])} - "
                f"<strong style='color:{color(step['status'])}'>{escape(step['status'])}</strong>"
                f"{err}</div>"
            )

        parts.append("</div>")

    parts.append("</body></html>")
    p.write_text("".join(parts), encoding="utf-8")
    return p