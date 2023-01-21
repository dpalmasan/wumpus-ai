from typing import Dict, Generator, List, Union
from inference.bayesian import Variable


class JointDistribution:
    def __init__(self) -> None:
        self._vars: List[Variable] = []
        self._probs = {}

    def all_events(
        self, vars: List[Variable], e: Dict[Variable, Union[str, bool, int]]
    ) -> Generator[Dict[Variable, Union[str, bool, int]], None, None]:
        if vars:
            var, rest = vars[0], vars[1:]
            for e_ in self.all_events(rest, e):
                for value in var.values:
                    extended_vars = e_.copy()
                    extended_vars[var] = value
                    yield extended_vars
        else:
            yield e
