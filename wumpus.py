from pylogic.propositional import (
    Variable,
    CnfClause,
)


class WumpusWorld:
    def __init__(self, grid):
        pass

    def _one_wumpus_rule_1(self, map_width: int = 4, map_height: int = 4):
        literals = set()
        for i in range(map_width):
            for j in range(map_height):
                literals.add(Variable(f"W{i}{j}", truthyness=True))

        return CnfClause(literals)

    def _one_wumpus_rule_2(self, map_width: int = 4, map_height: int = 4):
        cnf_clauses = set()
        for j in range(map_height):
            for i in range(map_width):
                if i > 0:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}", truthyness=False
                        ),
                        Variable(f"W{i - 1}{j}", truthyness=False)
                    ]))
                if i < map_width - 1:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}", truthyness=False
                        ),
                        Variable(f"W{i + 1}{j}", truthyness=False)
                    ]))
                if j > 0:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}", truthyness=False
                        ),
                        Variable(f"W{i}{j - 1}", truthyness=False)
                    ]))
                if j < map_height - 1:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}", truthyness=False
                        ),
                        Variable(f"W{i}{j + 1}", truthyness=False)
                    ]))
        return cnf_clauses

wumpus_world = WumpusWorld([])
print(wumpus_world._one_wumpus_rule_1())
print(wumpus_world._one_wumpus_rule_2())