# main.py
import importlib
import sys

from normalizer import compile_feature_model
from runner import run_scenarios
from report import write_json, write_html


def main():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python main.py <feature_file> <steps_module>")

    feature_file = sys.argv[1]
    steps_module = sys.argv[2]

    # load step definitions
    importlib.import_module(steps_module)

    exec_scenarios = compile_feature_model(feature_file)
    result = run_scenarios(exec_scenarios)

    json_path = write_json(result)
    html_path = write_html(result)

    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()