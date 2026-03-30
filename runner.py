# runner.py
from __future__ import annotations
from types import SimpleNamespace
import traceback
from typing import Dict, List

from registry import registry, resolve_keyword
from normalizer import ExecutableScenario, ExecStep


def _invoke(func, context, params):
    if isinstance(params, dict):
        return func(context, **params)
    if isinstance(params, tuple):
        return func(context, *params)
    return func(context)


def run_scenarios(exec_scenarios: List[ExecutableScenario]) -> Dict:
    """Execute a set of compiled scenarios and return a feature-level report dict."""
    if not exec_scenarios:
        return {"feature": "", "status": "passed", "scenarios": []}

    feature_name = exec_scenarios[0].feature_name
    feature_result = {
        "feature": feature_name,
        "status": "passed",
        "scenarios": [],
    }

    for sc in exec_scenarios:
        ctx = SimpleNamespace()
        prev_effective = None
        stop = False

        scenario_result = {
            "name": sc.scenario_name,
            "rule": sc.rule_name,
            "status": "passed",
            "source": sc.source,
            "steps": [],
        }

        for st in sc.steps:  # type: ExecStep
            raw_kw = st.keyword
            # * / And / But need to inherit the previous main keyword
            effective_kw = resolve_keyword(raw_kw, prev_effective)
            if raw_kw not in ("And", "But", "*"):
                prev_effective = effective_kw

            if stop:
                scenario_result["steps"].append(
                    {
                        "keyword": raw_kw,
                        "effective_keyword": effective_kw,
                        "text": st.text,
                        "status": "skipped",
                        "error": "",
                    }
                )
                continue

            try:
                func, params = registry.match(effective_kw, st.text)
                _invoke(func, ctx, params)
                scenario_result["steps"].append(
                    {
                        "keyword": raw_kw,
                        "effective_keyword": effective_kw,
                        "text": st.text,
                        "status": "passed",
                        "error": "",
                    }
                )
            except Exception as e:  # Match failed or assertion failed
                feature_result["status"] = "failed"
                scenario_result["status"] = "failed"
                stop = True
                scenario_result["steps"].append(
                    {
                        "keyword": raw_kw,
                        "effective_keyword": effective_kw,
                        "text": st.text,
                        "status": "failed",
                        "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc(limit=3),
                    }
                )

        feature_result["scenarios"].append(scenario_result)

    return feature_result