from inference.bayesian import (
    ConditionalProbabilityTable,
    BayesianNetwork,
    BayesianNetworkNode,
    Variable,
    enumeration_ask,
)
from inference.probability import JointDistribution

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

# Expected result
# {False: 0.7158281646356071, True: 0.2841718353643929}
print(res)

bn = BayesianNetwork(
    [
        BayesianNetworkNode(
            Variable("c", [False, True]),
            ConditionalProbabilityTable({(True,): 0.8,}, ("c",)),
        ),
        BayesianNetworkNode(
            Variable("r", [False, True]),
            ConditionalProbabilityTable({(True,): 0.8, (False,): 0.1}, ("c",)),
        ),
        BayesianNetworkNode(
            Variable("s", [False, True]),
            ConditionalProbabilityTable({(True,): 0.1, (False,): 0.5}, ("c",)),
        ),
        BayesianNetworkNode(
            Variable("g", [False, True]),
            ConditionalProbabilityTable(
                {
                    (True, True): 0.99,
                    (True, False): 0.9,
                    (False, True): 0.9,
                    (False, False): 0,
                },
                ("s", "r"),
            ),
        ),
    ]
)

# Expected {False: 0.2547999999999999, True: 0.7452}
x = Variable("g", [False, True])
e = {
    "c": True,
}

res = enumeration_ask(x, e, bn)
print(res)

bn = BayesianNetwork(
    [
        BayesianNetworkNode(
            Variable("r", [False, True]),
            ConditionalProbabilityTable({(True,): 0.2}, ("r",)),
        ),
        BayesianNetworkNode(
            Variable("s", [False, True]),
            ConditionalProbabilityTable({(True,): 0.01, (False,): 0.4}, ("r",)),
        ),
        BayesianNetworkNode(
            Variable("g", [False, True]),
            ConditionalProbabilityTable(
                {
                    (True, True): 0.99,
                    (True, False): 0.9,
                    (False, True): 0.8,
                    (False, False): 0,
                },
                ("s", "r"),
            ),
        ),
    ]
)

x = Variable("r", [False, True])
e = {
    "g": True,
}

# Expected result {False: 0.6423123243677238, True: 0.3576876756322762}
res = enumeration_ask(x, e, bn)
print(res)


v1 = Variable("A", [1, 2, 3])
v2 = Variable("B", [True, False])
v3 = Variable("C", ["cat", "dog"])

jpd = JointDistribution([v1, v2])
for events in jpd.all_events([v1, v3], {v2: True}):
    print(events)