from ast import Tuple
from collections import defaultdict
from functools import reduce
from random import random, randrange
from typing import Dict, List
from consts import Property
from pylogic.propositional import (
    Variable,
    Clause,
    BicondClause
)
from utils import Point

MAX_TRAPS_RATIO = 0.2
TRAPS_GOLD_INCIDENCE_RATE = 0.15


class WumpusWorld:
    def __init__(self, grid):
        self._grid = grid

    def __getitem__(self, key):
        return self._grid[key]

    def _one_wumpus_rule(self) -> Clause:
        """There should exist one wumpus."""
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        literals: List[Variable] = []
        for i in range(map_width):
            for j in range(map_height):
                literals.append(Variable(f"W{i}{j}", is_negated=False, truthyness=None))

        return reduce(lambda x, y: x | y, literals)

    def _at_most_one_wumpus(self) -> Clause:
        """There must be just one Wumpus."""
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        clauses = []
        for j in range(map_height):
            for i in range(map_width):
                if i > 0:
                    clauses.append(
                        Variable(f"W{i}{j}", is_negated=True, truthyness=None)
                        | Variable(f"W{i - 1}{j}", is_negated=True, truthyness=None)
                    )
                if i < map_width - 1:
                    clauses.append(
                        Variable(f"W{i}{j}", is_negated=True, truthyness=None)
                        | Variable(f"W{i + 1}{j}", is_negated=True, truthyness=None)
                    )
                if j > 0:
                    clauses.append(
                        Variable(f"W{i}{j}", is_negated=True, truthyness=None)
                        | Variable(f"W{i}{j - 1}", is_negated=True, truthyness=None)
                    )

                if j < map_height - 1:
                    if j > 0:
                        clauses.append(
                            Variable(f"W{i}{j}", is_negated=True, truthyness=None)
                            | Variable(f"W{i}{j + 1}", is_negated=True, truthyness=None)
                        )
        return reduce(lambda x, y: x & y, clauses)

    def _breeze_stench_rules(self):
        map_width = len(self._grid[0])
        map_height = len(self._grid)
        clauses = defaultdict(list)
        for i in range(map_width):
            for j in range(map_height):
                b = Variable(f"B{i}{j}", False)
                s = Variable(f"S{i}{j}", False)
                p1 = None
                w1 = None
                if i > 0:
                    p1 = Variable(f"P{i-1}{j}", False)
                    w1 = Variable(f"W{i-1}{j}", False)

                p2 = None
                w2 = None
                if i < map_width - 1:
                    p2 = Variable(f"P{i+1}{j}", False)
                    w2 = Variable(f"W{i+1}{j}", False)
                p3 = None
                w3 = None
                if j > 0:
                    p3 = Variable(f"P{i}{j-1}", False)
                    w3 = Variable(f"W{i}{j-1}", False)
                p4 = None
                w4 = None
                if j < map_height - 1:
                    p4 = Variable(f"P{i}{j + 1}", False)
                    w4 = Variable(f"W{i}{j + 1}", False)

                p = reduce(
                    lambda x, y: x | y,
                    filter(lambda x: x is not None, [p1, p2, p3, p4]),
                )
                w = reduce(
                    lambda x, y: x | y,
                    filter(lambda x: x is not None, [w1, w2, w3, w4]),
                )
                clauses["B", Point(i, j)].append(BicondClause(b, p))
                clauses["S", Point(i, j)].append(BicondClause(s, w))
        return clauses


def create_wumpus_world(map_width=4, map_height=4):
    grid = [[set() for i in map_width] for j in map_height]
    # can write a function for this type of random coord generation (nothing should be on 0,0)
    wumpus_location = randrange(1, map_width * map_height)
    wumpus_y = int(wumpus_location / map_width)
    wumpus_x = wumpus_location - (wumpus_y * map_width)
    grid[wumpus_y][wumpus_x].add(set([Property.WUMPUS]))
    # can maybe use breeze stench rules to simplify this? or abstract into a function
    if wumpus_x > 0:
        if wumpus_y > 0:
            grid[wumpus_y - 1][wumpus_x - 1].add([Property.STENCH])
        if wumpus_y < map_height - 1:
            grid[wumpus_y + 1][wumpus_x - 1].add([Property.STENCH])
    if wumpus_x < map_width - 1:
        if wumpus_y > 0:
            grid[wumpus_y - 1][wumpus_x + 1].add([Property.STENCH])
        if wumpus_y < map_height - 1:
            grid[wumpus_y + 1][wumpus_x + 1].add([Property.STENCH])

    max_traps_threshold = int(map_width * map_height * MAX_TRAPS_RATIO)
    trap_locations = []
    for i in range (map_width * map_height):
        y = int(i / map_width)
        x = i - (y * map_width)
        if random(1) > TRAPS_GOLD_INCIDENCE_RATE: # tied to same rate for simplicity
            grid[y][x].add([Property.GOLD])
        if random(1) > TRAPS_GOLD_INCIDENCE_RATE and len(trap_locations) < max_traps_threshold:
            grid[y][x].add([Property.PIT])
            trap_locations.append([x, y])

    for loc in trap_locations:
        trap_x, trap_y = loc[0], loc[1]
        if trap_x > 0:
            if trap_y > 0:
                grid[trap_y - 1][trap_x - 1].add([Property.STENCH])
            if wumpus_y < map_height - 1:
                grid[trap_y + 1][trap_x - 1].add([Property.STENCH])
        if trap_x < map_width - 1:
            if wumpus_y > 0:
                grid[trap_y - 1][trap_x + 1].add([Property.STENCH])
            if wumpus_y < map_height - 1:
                grid[trap_y + 1][trap_x + 1].add([Property.STENCH])

    return WumpusWorld(grid)



def create_wumpus_world1():
    return WumpusWorld(
        [
            [set([Property.STENCH]), set(), set([Property.BREEZE]), set([Property.PIT])],
            [set([Property.WUMPUS]), set([Property.BREEZE, Property.STENCH, Property.GOLD]), set([Property.PIT]), set([Property.BREEZE])],
            [set([Property.STENCH]), set(), set([Property.BREEZE]), set()],
            [set(), set([Property.BREEZE]), set([Property.PIT]), set([Property.BREEZE])],
        ]
    )


def create_wumpus_world2():
    return WumpusWorld(
        [
            [set([Property.GOLD]), set(), set(), set()],
            [set(), set(), set([Property.BREEZE]), set([Property.PIT])],
            [set([Property.STENCH]), set([Property.WUMPUS]), set(), set([Property.PIT])],
            [set(), set([Property.STENCH]), set(), set([Property.BREEZE])],
        ]
    )
