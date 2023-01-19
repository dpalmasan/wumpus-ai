from typing import Any, Dict, List, Optional, Tuple


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
        return item in self._probs

    def __repr__(self) -> str:
        return "\n".join(f"{row}: {value}" for row, value in self._probs.items())

    def __getitem__(self, item):
        return self._probs[item]

    def __iter__(self):
        yield from self._probs.items()


class Variable:
    def __init__(self, name: str, values: List[Any]) -> None:
        self._name = name
        self._values = sorted(values)

    @property
    def name(self) -> str:
        return self._name

    @property
    def values(self) -> List[Any]:
        return self._values

    def __repr__(self) -> str:
        return f"{self.name} {self.values}"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.values == other.values

    def __iter__(self) -> Any:
        yield from self.values


class BayesianNetworkNode:
    def __init__(
        self,
        var: Variable,
        cpt: ConditionalProbabilityTable,
    ):
        self._var = var
        self._cpt = cpt

    @property
    def var(self) -> Variable:
        return self._var

    @property
    def cpt(self):
        return self._cpt

    def is_independent_var(self) -> bool:
        return self.cpt.n_vars == 1 and self.cpt.varnames[0] == self.var.name

    def __iter__(self):
        yield from self._var


class BayesianNetwork:
    def __init__(self, nodes: List[BayesianNetworkNode]) -> None:
        self._vars = [node for node in nodes]

    @property
    def vars(self) -> List[BayesianNetworkNode]:
        return self._vars


def enumeration_ask(x: Variable, e: Dict[str, Any], bn: BayesianNetwork):
    q = {}
    for xi in x:
        ex = e.copy()
        ex[x.name] = xi
        q[xi] = enumerate_all(bn.vars, ex)

    # Normalize distribution
    norm_den = sum(q.values())
    for key in q:
        q[key] /= norm_den
    return q


def enumerate_all(vars: List[BayesianNetworkNode], e: Dict[str, Any]) -> float:
    """Compute probability distribution of a variable given observed values.

    TODO: Optimize memory usage, as to get the correct result we are
    creating copies of observed values

    :param vars: Variables with their CPT
    :type vars: List[BayesianNetworkNode]
    :param e: Observed values
    :type e: Dict[str, Any]
    :return: Conditional probability
    :rtype: float
    """
    if len(vars) == 0:
        return 1
    y = vars[0]
    if y.var.name in e:
        if y.is_independent_var():
            py = y.cpt[(True,)]
            if not e[y.var.name]:
                py = 1 - py
            return py * enumerate_all(vars[1:], e)

        parent = tuple(e[p] for p in y.cpt.varnames)
        py = y.cpt[parent]
        if not e[y.var.name]:
            py = 1 - py
        return py * enumerate_all(vars[1:], e)

    sum = 0
    if y.is_independent_var():
        ey = e.copy()
        ey[y.var.name] = True
        sum += y.cpt[(True,)] * enumerate_all(vars[1:], ey)
        ey = e.copy()
        ey[y.var.name] = False
        sum += (1 - y.cpt[(True,)]) * enumerate_all(vars[1:], ey)
        return sum

    parent = tuple(e[p] for p in y.cpt.varnames)
    ey = e.copy()
    ey[y.var.name] = True
    sum += y.cpt[parent] * enumerate_all(vars[1:], ey)
    ey = e.copy()
    ey[y.var.name] = False
    sum += (1 - y.cpt[parent]) * enumerate_all(vars[1:], ey)
    return sum
