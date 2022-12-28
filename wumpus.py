from functools import reduce
from pylogic.propositional import (
    Variable,
    CnfClause,
    CnfParser,
    to_cnf,
)


class WumpusWorld:
    def __init__(self, grid):
        self._grid = grid

    def __getitem__(self, key):
        return self._grid[key]

    def _one_wumpus_rule(self):
        """There should exist one wumpus."""
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        literals = set()
        for i in range(map_width):
            for j in range(map_height):
                literals.add(Variable(f"W{i}{j}", truthyness=True))

        return CnfClause(literals)

    def _at_most_one_wumpus(self):
        """There must be just one Wumpus."""
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        cnf_clauses = set()
        for j in range(map_height):
            for i in range(map_width):
                if i > 0:
                    cnf_clauses.add(
                        CnfClause(
                            set([
                                Variable(f"W{i}{j}", truthyness=False),
                                Variable(f"W{i - 1}{j}", truthyness=False),
                            ])
                        )
                    )
                if i < map_width - 1:
                    cnf_clauses.add(
                        CnfClause(
                            set([
                                Variable(f"W{i}{j}", truthyness=False),
                                Variable(f"W{i + 1}{j}", truthyness=False),
                            ])
                        )
                    )
                if j > 0:
                    cnf_clauses.add(
                        CnfClause(
                            set([
                                Variable(f"W{i}{j}", truthyness=False),
                                Variable(f"W{i}{j - 1}", truthyness=False),
                            ])
                        )
                    )
                if j < map_height - 1:
                    cnf_clauses.add(
                        CnfClause(
                            set([
                                Variable(f"W{i}{j}", truthyness=False),
                                Variable(f"W{i}{j + 1}", truthyness=False),
                            ])
                        )
                    )
        return cnf_clauses

    def _breeze_stench_rules(self):
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        cnf_clauses = set()
        parser = CnfParser()
        for i in range(map_width):
            for j in range(map_height):
                b = Variable(f"B{i}{j}", True)
                s = Variable(f"S{i}{j}", True)
                p1 = None
                w1 = None
                if i > 0:
                    p1 = Variable(f"P{i-1}{j}", True)
                    w1 = Variable(f"W{i-1}{j}", True)

                p2 = None
                w2 = None
                if i < map_width - 1:
                    p2 = Variable(f"P{i+1}{j}", True)
                    w2 = Variable(f"W{i+1}{j}", True)
                p3 = None
                w3 = None
                if j > 0:
                    p3 = Variable(f"P{i}{j-1}", True)
                    w3 = Variable(f"W{i}{j-1}", True)
                p4 = None
                w4 = None
                if j < map_height - 1:
                    p4 = Variable(f"P{i}{j + 1}", True)
                    w4 = Variable(f"W{i}{j + 1}", True)

                p = reduce(
                    lambda x, y: x | y,
                    filter(lambda x: x is not None, [p1, p2, p3, p4]),
                )
                w = reduce(
                    lambda x, y: x | y,
                    filter(lambda x: x is not None, [w1, w2, w3, w4]),
                )
                cnf = to_cnf(b >> p)
                cnf_clauses |= parser.parse(cnf)
                cnf = to_cnf(s >> w)
                cnf_clauses |= parser.parse(cnf)
        return cnf_clauses

def create_wumpus_world():
    return WumpusWorld(
        [
            [set("S"), set(), set("B"), set("P")],
            [set("W"), set(["B", "S", "G"]), set("P"), set("B")],
            [set("S"), set(), set("B"), set()],
            [set(), set("B"), set("P"), set("B")],
        ]
    )
