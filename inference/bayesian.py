from typing import Dict, List, Optional, Tuple


class InvalidCPTException(Exception):
    pass


class ConditionalProbabilityTable:
    def __init__(self, probs: Dict[Tuple[bool], float], varnames: Tuple[str]) -> None:
        self._probs = probs
        for row in probs:
            n_vars = len(row)
            break
        if len(varnames) != n_vars:
            raise InvalidCPTException(
                "Provided varnames should have "
                f"the same length as CPT rows: {varnames} {probs}"
            )
        self._nvars = n_vars
        self._varnames = varnames

    @property
    def probs(self):
        return self._probs

    @property
    def n_vars(self) -> int:
        return self._nvars

    @property
    def varnames(self) -> Tuple[str]:
        return self._varnames

    def __contains__(self, item: str) -> bool:
        return item in self.varnames

    def __repr__(self) -> str:
        return "\n".join(f"{row}: {value}" for row, value in self._probs.items())


class BayesianNetworkNode:
    def __init__(
        self,
        varname: str,
        cpt: ConditionalProbabilityTable,
        parents: Optional[List["BayesianNetworkNode"]] = None,
    ):
        self._varname = varname
        self.cpt = cpt
        self._parents = []
        if parents is not None:
            self._parents = parents
        assert len(self._parents) == self.cpt.n_vars

    @property
    def parents(self) -> List["BayesianNetworkNode"]:
        return list(self._parents)

    @property
    def varname(self) -> str:
        return self._varname


class BayesianNetwork:
    def __init__(self, nodes: Dict[str, BayesianNetworkNode]) -> None:
        self._nodes = nodes
        self._vars = [var for var in self._nodes.items()]

    @property
    def nodes(self) -> Dict[str, float]:
        return self._nodes

    @property
    def vars(self) -> List[str]:
        return self._vars


# Test case
cpt = ConditionalProbabilityTable(
    {
        (True, True): 0.95,
        (True, False): 0.94,
        (False, True): 0.29,
        (False, False): 0.001,
    },
    ("p", "j")
)

print(cpt, "p" in cpt, "a" in cpt)

def enumeration_ask(x, e, bn: BayesianNetwork):
    q = {}
    for xi in bn[x]:
        exi = e.copy()
        exi[xi] = x[xi]
        q[xi] = enumerate_all(bn.vars, exi)

    return q


def enumerate_all(vars, e) -> float:
    if len(vars) == 0:
        return 1
    y = vars[0]
    if any(yi in e for yi in y):
        return y * enumerate_all(vars[1:], e)

    sum = 0

    return 0
