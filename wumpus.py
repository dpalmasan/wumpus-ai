from pylogic.propositional import (
    Variable,
    CnfClause,
)


class WumpusWorld:
    def __init__(self, grid):
        pass

    def _one_wumpus_rule_1(self):
        literals = set()
        # TODO: Update for any size wumpus grid
        for i in range(4):
            for j in range(4):
                literals.add(Variable(f"W{i}{j}"))

        return CnfClause(literals)

    def _one_wumpus_rule_2():
        cnf_clauses = set()
        for i in range(4):
            for j in range(4):
                if i > 0:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}"
                        ),
                        Variable(f"W{i - 1}{j}")
                    ]))
                if i < 3:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}"
                        ),
                        Variable(f"W{i + 1}{j}")
                    ]))
                if j > 0:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}"
                        ),
                        Variable(f"W{i}{j - 1}")
                    ]))
                if j < 3:
                    cnf_clauses.add(CnfClause([
                        Variable(
                            f"W{i}{j}"
                        ),
                        Variable(f"W{i}{j + 1}")
                    ]))
        return cnf_clauses
                


