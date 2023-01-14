from typing import Dict


class BayesianNetwork:
    def __init__(self, nodes: Dict[str, float]) -> None:
        self._nodes = dict(nodes)

    @property
    def nodes(self) -> Dict[str, float]:
        return dict(self._nodes)