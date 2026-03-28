from types import SimpleNamespace
import traceback
from registry import registry, resolve_keyword


def _invoke(func, context, params):
    if isinstance(params, dict):
        return func(context, **params)
    if isinstance(params, tuple):
        return func(context, *params)
    return func(context)


def run_feature(model):
    feature_result = {
        "feature": model.feature.name.strip(),
        "status": "passed",
        "scenarios": []
    }

    for scenario in model.feature.scenarios:
        ctx = SimpleNamespace()
        prev = None
        stop = False

        scenario_result = {
            "name": scenario.name.strip(),
            "status": "passed",
            "steps": []
        }

        for st in scenario.steps:
            effective = resolve_keyword(st.keyword, prev)
            prev = effective

            if stop:
                scenario_result["steps"].append({
                    "keyword": st.keyword,
                    "effective_keyword": effective,
                    "text": st.text.strip(),
                    "status": "skipped",
                    "error": ""
                })
                continue

            try:
                func, params = registry.match(effective, st.text)
                _invoke(func, ctx, params)
                scenario_result["steps"].append({
                    "keyword": st.keyword,
                    "effective_keyword": effective,
                    "text": st.text.strip(),
                    "status": "passed",
                    "error": ""
                })
            except Exception as e:
                feature_result["status"] = "failed"
                scenario_result["status"] = "failed"
                stop = True
                scenario_result["steps"].append({
                    "keyword": st.keyword,
                    "effective_keyword": effective,
                    "text": st.text.strip(),
                    "status": "failed",
                    "error": f"{type(e).__name__}: {e}",
                    "trace": traceback.format_exc(limit=3)
                })

        feature_result["scenarios"].append(scenario_result)

    return feature_result