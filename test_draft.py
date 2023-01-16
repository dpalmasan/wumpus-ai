from inference.bayesian import (
    ConditionalProbabilityTable,
    BayesianNetwork,
    BayesianNetworkNode,
    Variable,
    enumeration_ask,
)

e = {
    "j": True,
    "m": True,
}

# Test case
cpt = ConditionalProbabilityTable(
    {
        (True, True): 0.95,
        (True, False): 0.94,
        (False, True): 0.29,
        (False, False): 0.001,
    },
    ("b", "e"),
)

bn = BayesianNetwork(
    [
        BayesianNetworkNode(
            Variable("e", [False, True]),
            ConditionalProbabilityTable({(True,): 0.002}, ("e",)),
        ),
        BayesianNetworkNode(
            Variable("b", [False, True]),
            ConditionalProbabilityTable({(True,): 0.001}, ("b",)),
        ),
        BayesianNetworkNode(Variable("a", [False, True]), cpt),
        BayesianNetworkNode(
            Variable("j", [False, True]),
            ConditionalProbabilityTable({(True,): 0.9, (False,): 0.05}, ("a",)),
        ),
        BayesianNetworkNode(
            Variable("m", [False, True]),
            ConditionalProbabilityTable({(True,): 0.7, (False,): 0.01}, ("a",)),
        ),
    ]
)

x = Variable("b", [False, True])

res = enumeration_ask(x, e, bn)

print(res)