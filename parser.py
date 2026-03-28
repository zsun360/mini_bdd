from functools import lru_cache
from pathlib import Path
from textx import metamodel_from_file

@lru_cache(maxsize=1)
def get_metamodel():
    grammar = Path(__file__).with_name("gherkin.tx")
    return metamodel_from_file(str(grammar))

def load_feature(feature_path: str):
    return get_metamodel().model_from_file(feature_path)