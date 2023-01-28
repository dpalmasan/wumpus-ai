from ast import Tuple
from collections import defaultdict
from functools import reduce
from random import random, choice
from typing import Dict, List
from consts import Property
from pylogic.propositional import (
    Variable,
    Clause,
    BicondClause
)
from utils import Point

MAX_TRAPS_RATIO = 0.2
TRAPS_INCIDENCE_RATE = 0.15


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


class WumpusWorldGenerator:
    def __init__(self, map_width=4, map_height=4):
        self._map_width = map_width
        self._map_height = map_height
        self._occupied_spaces = []
        self._generate_random_wumpus()


    def _spawn_object_coords(self):
        grid_size = self._map_width * self._map_height
        max_range = list(range(grid_size)) # Nothing should be on 0,0
        acceptable_range = list(set(max_range) - set(self._occupied_spaces))
        # this can technically break if we change max_traps_ratio and no spots are left
        object_location = choice(acceptable_range)
        self._occupied_spaces.append(object_location)
        y = int(object_location / self._map_width)
        x = object_location - (y * self._map_width)
        return(x, y)


    def _adjacent_coords(self, x, y):
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in dirs:
            xnew, ynew = x - dx, y - dy
            if self._valid_coord(xnew, ynew):
                yield xnew, ynew


    def _valid_coord(self, x, y) -> bool:
        return (x >= 0 and x < self._map_width and y >= 0 and y < self._map_height)


    @property
    def _traps_incidence_rate(self):
        return TRAPS_INCIDENCE_RATE


    @property
    def _max_traps_ratio(self):
        return MAX_TRAPS_RATIO


    def _generate_random_wumpus(self):
        grid = [
            [set() for _ in range(self._map_width)] for _ in range(self._map_height)
        ]
        self._occupied_spaces.append(0) # player spawns here
        wumpus_x, wumpus_y = self._spawn_object_coords()
        grid[wumpus_y][wumpus_x].add(Property.WUMPUS)
        for coord in self._adjacent_coords(wumpus_x, wumpus_y):
            x, y = coord[0], coord[1]
            grid[y][x].add(Property.STENCH)

        max_traps_threshold = int(
            self._map_width * self._map_height * self._max_traps_ratio
        )
        num_traps = int(
            min(
                max_traps_threshold,
                sum(
                    random() > self._traps_incidence_rate
                    for _ in range(self._map_width * self._map_height)
                ),
            )
        )

        trap_locations = []
        for _ in range(num_traps):
            trap_x, trap_y = self._spawn_object_coords()
            grid[trap_y][trap_x].add(Property.PIT)
            trap_locations.append([trap_x, trap_y])

        gold_x, gold_y = self._spawn_object_coords()
        grid[gold_y][gold_x].add(Property.GOLD)

        for loc in trap_locations:
            trap_x, trap_y = loc[0], loc[1]
            for coord in self._adjacent_coords(trap_x, trap_y):
                x, y = coord[0], coord[1]
                grid[y][x].add(Property.BREEZE)

        self.world = WumpusWorld(grid)


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
