from dataclasses import dataclass, field

@dataclass
class ExecStep:
    keyword: str
    text: str
    source: dict = field(default_factory=dict)

@dataclass
class ExecutableScenario:
    feature_name: str
    rule_name: str | None
    scenario_name: str
    steps: list[ExecStep]
    source: dict = field(default_factory=dict)