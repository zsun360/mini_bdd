# normalizer.py
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from parser import load_feature

# -------- helper function  --------

@dataclass
class ExecStep:
    keyword: str
    text: str
    source: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutableScenario:
    feature_name: str
    rule_name: Optional[str]
    scenario_name: str
    steps: List[ExecStep]
    source: Dict[str, Any] = field(default_factory=dict)

# -------- helper function  --------

PARAM_RE = re.compile(r"<([^>]+)>")

def _steps_to_exec(steps) -> List[ExecStep]:
    """Convert the list of textX Steps into a list of ExecSteps."""
    result: List[ExecStep] = []
    for s in steps:
        result.append(
            ExecStep(
                keyword=s.keyword,
                text=s.text.strip(),
                source={"raw_keyword": s.keyword, "raw_text": s.text},
            )
        )
    return result


def _table_to_row_dicts(table) -> List[Dict[str, str]]:
    """Convert ExamplesTable into [{col: value}, ...]."""
    headers = [c.strip() for c in table.header.cells]
    rows: List[Dict[str, str]] = []
    for row in table.rows:
        values = [c.strip() for c in row.cells]
        rows.append(dict(zip(headers, values)))
    return rows


def _substitute_params(text: str, row: Dict[str, str]) -> str:
    """Substitute <param> with the value from the row."""

    def repl(m: re.Match) -> str:
        key = m.group(1)
        if key not in row:
            raise KeyError(f"Missing Examples column: {key}")
        return row[key]

    return PARAM_RE.sub(repl, text)


def _expand_outline(
    feature_name: str,
    rule_name: Optional[str],
    outline,
    inherited_steps: List[ExecStep],
) -> List[ExecutableScenario]:
    """Expand a Scenario Outline by all Examples rows."""
    result: List[ExecutableScenario] = []
    base_steps = _steps_to_exec(outline.steps)

    for examples_index, ex in enumerate(outline.examples, start=1):
        row_dicts = _table_to_row_dicts(ex.table)
        ex_name = getattr(ex, "name", None) or ""

        for row_index, row in enumerate(row_dicts, start=1):
            expanded_steps: List[ExecStep] = []
            for s in base_steps:
                expanded_steps.append(
                    ExecStep(
                        keyword=s.keyword,
                        text=_substitute_params(s.text, row),
                        source={
                            "template_text": s.text,
                            "row": row,
                            "examples_name": ex_name,
                        },
                    )
                )

            scenario_label = f"{outline.name.strip()} [{examples_index}.{row_index}]"
            result.append(
                ExecutableScenario(
                    feature_name=feature_name,
                    rule_name=rule_name,
                    scenario_name=scenario_label,
                    steps=[*inherited_steps, *expanded_steps],
                    source={
                        "kind": "outline",
                        "outline_name": outline.name.strip(),
                        "examples_name": ex_name,
                        "examples_index": examples_index,
                        "row_index": row_index,
                        "row_data": row,
                    },
                )
            )

    return result


# -------- Main entry: Compile Feature model into a list of ExecutableScenarios --------

def compile_feature_model(feature_path: str) -> List[ExecutableScenario]:
    """Obtain all executable scenarios directly from the .feature file."""
    model = load_feature(feature_path)
    f = model.feature

    feature_name = f.name.strip()
    feature_bg = _steps_to_exec(f.background.steps) if f.background else []

    executable: List[ExecutableScenario] = []

    for item in f.items:
        cls_name = item.__class__.__name__

        if cls_name == "Scenario":
            executable.append(
                ExecutableScenario(
                    feature_name=feature_name,
                    rule_name=None,
                    scenario_name=item.name.strip(),
                    steps=[*feature_bg, *_steps_to_exec(item.steps)],
                    source={"kind": "scenario"},
                )
            )

        elif cls_name == "ScenarioOutline":
            executable.extend(
                _expand_outline(feature_name, None, item, feature_bg)
            )

        elif cls_name == "Rule":
            rule_name = item.name.strip()
            rule_bg = _steps_to_exec(item.background.steps) if item.background else []
            inherited = [*feature_bg, *rule_bg]

            for sub in item.items:
                sub_cls = sub.__class__.__name__

                if sub_cls == "Scenario":
                    executable.append(
                        ExecutableScenario(
                            feature_name=feature_name,
                            rule_name=rule_name,
                            scenario_name=sub.name.strip(),
                            steps=[*inherited, *_steps_to_exec(sub.steps)],
                            source={"kind": "scenario", "rule": rule_name},
                        )
                    )
                elif sub_cls == "ScenarioOutline":
                    executable.extend(
                        _expand_outline(feature_name, rule_name, sub, inherited)
                    )

    return executable