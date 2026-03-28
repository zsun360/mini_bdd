import re


class StepRegistry:
    def __init__(self):
        self._defs = {
            "given": [],
            "when": [],
            "then": [],
            "step": [],
        }

    def register(self, step_type, pattern):
        regex = re.compile(pattern)

        def decorator(func):
            self._defs[step_type].append({
                "regex": regex,
                "func": func,
                "pattern": pattern
            })
            return func

        return decorator

    def match(self, step_type, text):
        candidates = [*self._defs.get(step_type, []), *self._defs["step"]]
        for item in candidates:
            m = item["regex"].fullmatch(text.strip())
            if m:
                params = m.groupdict() or m.groups()
                return item["func"], params
        raise LookupError(f"No step definition matched: [{step_type}] {text}")


registry = StepRegistry()


def _make(step_type):
    return lambda pattern: registry.register(step_type, pattern)


given = _make("given")
when = _make("when")
then = _make("then")
step = _make("step")


def resolve_keyword(keyword, previous_effective):
    k = keyword.lower()
    if k in {"and", "but"}:
        if previous_effective is None:
            raise ValueError(f"{keyword} cannot be the first step.")
        return previous_effective
    return k