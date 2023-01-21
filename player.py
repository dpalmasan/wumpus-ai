from abc import abstractmethod
from enum import Enum
import pickle
import random
from typing import Optional, Tuple
from pylogic.propositional import (
    Variable,
    CnfClause,
    DpllKB,
    ResolutionKB,
    pl_resolution,
    CnfParser,
    to_cnf,
)
from inference import probability

import os

from wumpus import WumpusWorld, create_wumpus_world

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from utils import Point, ShortestPathSearchProblem, a_star_route, manhattan_heuristic


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class NoAvailableSafeTiles(Exception):
    pass


class Player:
    def __init__(self, pos: Point):
        self._pos = pos

    @property
    def pos(self) -> Point:
        return self._pos

    @abstractmethod
    def update(self) -> None:
        raise NotImplemented()

    def draw(self, canvas, rect, color) -> None:
        pygame.draw.rect(canvas, color, rect, 1)


class LogicAIPlayer(Player):
    def __init__(self, pos: Point, wumpus_world: WumpusWorld, kb_type="dpll") -> None:
        Player.__init__(
            self,
            pos,
        )
        self._pos = pos
        self._kb = DpllKB()
        self._visited = []
        for _ in range(len(wumpus_world._grid)):
            self._visited.append([False] * len(wumpus_world[0]))

        self._wumpus_world = wumpus_world
        self._fringe = set()
        self._plan = []
        self._kb.add(Variable(f"W{pos.x}{pos.y}", True))
        self._kb.add(Variable(f"P{pos.x}{pos.y}", True))
        self._breeze_stench_rules = wumpus_world._breeze_stench_rules()
        for y in range(len(self._visited)):
            for x in range(len(self._visited[y])):
                for clause in self._breeze_stench_rules["B", Point(x, y)]:
                    self._kb.add(clause)
                for clause in self._breeze_stench_rules["S", Point(x, y)]:
                    self._kb.add(clause)

    def _is_adjacent(self, x1, y1, x2, y2) -> bool:
        return (
            (x1 == x2 - 1 and y2 == y1)
            or (x1 == x2 + 1 and y2 == y1)
            or (x1 == x2 and y2 == y1 - 1)
            or (x1 == x2 and y2 == y1 + 1)
            or (x1 - 1 == x2 and y2 == y1)
            or (x1 + 1 == x2 and y2 == y1)
            or (x1 == x2 and y2 - 1 == y1)
            or (x1 == x2 and y2 + 1 == y1)
            or (x1 == x2 and y1 == y2)
        )

    def _pl_wumpus_agent(self) -> Direction:
        x, y = self.pos.x, self.pos.y
        self._perceive()
        self._visited[y][x] = True
        self._update_fringe()

        debug = []
        for row in self._visited:
            debug.append(["0"] * len(row))
        debug[self.pos.y][self.pos.x] = "x"
        for row in debug:
            print(row)

        if "W" in self._wumpus_world[y][x] or "P" in self._wumpus_world[y][x]:
            raise Exception("YOU DIED!")
        elif "G" in self._wumpus_world[y][x]:
            raise Exception("YOU WON!")

        if len(self._plan):
            action = self._plan.pop(0)
            if action == "up":
                action = Direction.UP
            elif action == "down":
                action = Direction.DOWN
            elif action == "left":
                action = Direction.LEFT
            else:
                action = Direction.RIGHT
            yield action
        else:
            safe_pos = self._get_safe_pos()
            if safe_pos is not None:
                self._plan = a_star_route(
                    ShortestPathSearchProblem(self.pos, safe_pos, self._visited)
                )

                action = self._plan.pop(0)
                if action == "up":
                    action = Direction.UP
                elif action == "down":
                    action = Direction.DOWN
                elif action == "left":
                    action = Direction.LEFT
                else:
                    action = Direction.RIGHT
                yield action

        yield self._random_move()

    def _check_if_no_pit(self, i, j) -> bool:
        p = Variable(f"P{i}{j}", is_negated=False, truthyness=None)
        return self._kb.query(~p)

    def _check_if_no_wumpus(self, i, j) -> bool:
        w = Variable(f"W{i}{j}", is_negated=False, truthyness=None)

        return self._kb.query(~w)

    def _get_safe_pos(self) -> Optional[Point]:
        for i, j in self._fringe:
            if self._check_if_no_pit(i, j) and self._check_if_no_wumpus(i, j):
                return Point(i, j)

        return None

    def _random_move(self) -> Direction:
        print("RANDOM")
        x, y = self.pos.x, self.pos.y
        choices = []
        if x > 0 and not self._visited[y][x - 1]:
            choices.append(Direction.LEFT)
        if x < len(self._wumpus_world._grid[0]) - 1 and not self._visited[y][x + 1]:
            choices.append(Direction.RIGHT)
        if y > 0 and not self._visited[y - 1][x]:
            choices.append(Direction.UP)
        if y < len(self._wumpus_world._grid) - 1 and not self._visited[y + 1][x]:
            choices.append(Direction.DOWN)

        return random.choice(choices)

    def _update_fringe(self) -> None:
        x, y = self.pos.x, self.pos.y
        if x > 0 and not self._visited[y][x - 1]:
            self._fringe.add((x - 1, y))
        if x < len(self._wumpus_world._grid[0]) - 1 and not self._visited[y][x + 1]:
            self._fringe.add((x + 1, y))
        if y > 0 and not self._visited[y - 1][x]:
            self._fringe.add((x, y - 1))
        if y < len(self._wumpus_world._grid) - 1 and not self._visited[y + 1][x]:
            self._fringe.add((x, y + 1))

        if (x, y) in self._fringe:
            self._fringe.remove((x, y))

    def _is_valid_pos(self) -> bool:
        x, y = self.pos.x, self.pos.y
        return (
            x >= 0
            and y >= 0
            and x <= len(self._wumpus_world._grid) - 1
            and y <= len(self._wumpus_world._grid) - 1
        )

    def _perceive(self):
        x, y = self.pos.x, self.pos.y
        if "S" in self._wumpus_world[y][x]:
            self._kb.add(Variable(f"S{x}{y}", is_negated=False, truthyness=None))
        else:
            self._kb.add(Variable(f"S{x}{y}", is_negated=True, truthyness=None))

        if "B" in self._wumpus_world[y][x]:
            self._kb.add(Variable(f"B{x}{y}", is_negated=False, truthyness=None))
        else:
            self._kb.add(Variable(f"B{x}{y}", is_negated=True, truthyness=None))

    def update(self):
        action = next(self._pl_wumpus_agent())
        pos = self.pos
        if action == Direction.UP:
            new_pos = Point(pos.x, pos.y - 1)
        elif action == Direction.DOWN:
            new_pos = Point(pos.x, pos.y + 1)
        elif action == Direction.LEFT:
            new_pos = Point(pos.x - 1, pos.y)
        else:
            new_pos = Point(pos.x + 1, pos.y)
        self._pos.update(new_pos)


class HumanPlayer(Player):
    def __init__(self, pos):
        Player.__init__(self, pos)

    def update(self, new_pos):
        self._pos = new_pos

    def __repr__(self) -> str:
        return f"HumanPlayer({self.pos}"


class ProbabilisticAIPlayer(Player):
    def __init__(self, pos: Point, wumpus_world: WumpusWorld):
        Player.__init__(self, pos)

        self._visited = []
        for _ in range(len(wumpus_world._grid)):
            self._visited.append([False] * len(wumpus_world[0]))

        self._wumpus_world = wumpus_world
        self._plan = []
        self._fringe = set()
        self._evidence_breeze_stench = {}
        self._known_pit_wumpus = {}

    def _is_valid_pos(self, x, y) -> bool:
        return (
            x >= 0
            and y >= 0
            and x <= len(self._wumpus_world._grid) - 1
            and y <= len(self._wumpus_world._grid) - 1
        )

    def _adjacent_positions(self, x, y):
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for x0, y0 in dirs:
            if self._is_valid_pos(x - x0, y - y0):
                yield x - x0, y - y0

    def _perceive(self):
        x, y = self.pos.x, self.pos.y
        if "S" in self._wumpus_world[y][x] or "B" in self._wumpus_world[y][x]:
            self._evidence_breeze_stench[(x, y)] = True
        else:
            self._known_pit_wumpus[(x, y)] = False
            self._evidence_breeze_stench[(x, y)] = False

        for xa, ya in self._adjacent_positions(x, y):
            if not self._visited[ya][xa]:
                self._fringe.add((xa, ya))

    def _probabilistic_agent(self):
        x, y = self.pos.x, self.pos.y
        self._visited[y][x] = True
        self._perceive()
        for row in self._visited:
            print(row)
        if (x, y) in self._fringe:
            self._fringe.remove((x, y))
        if len(self._plan):
            action = self._plan.pop(0)
            if action == "up":
                action = Direction.UP
            elif action == "down":
                action = Direction.DOWN
            elif action == "left":
                action = Direction.LEFT
            else:
                action = Direction.RIGHT
            yield action
        else:
            safe_pos = self._get_safe_pos()
            if safe_pos is not None:
                self._plan = a_star_route(
                    ShortestPathSearchProblem(self.pos, safe_pos, self._visited)
                )

                action = self._plan.pop(0)
                if action == "up":
                    action = Direction.UP
                elif action == "down":
                    action = Direction.DOWN
                elif action == "left":
                    action = Direction.LEFT
                else:
                    action = Direction.RIGHT
                yield action

    def _has_surrounding_pits_wumpus(self, event, x, y):
        for xa, ya in self._adjacent_positions(x, y):
            if (
                event.get((xa, ya), False)
                and (xa, ya) not in self._evidence_breeze_stench
            ):
                return True
        return False

    def _consistent(self, event) -> bool:
        for x, y in self._evidence_breeze_stench:
            # has breeze or stench but has no surrounding pit or wumpus
            if self._evidence_breeze_stench[
                (x, y)
            ] and not self._has_surrounding_pits_wumpus(event, x, y):
                return 0
            # Does not have breeze or stench but has surrounding pit or wumpus
            if not self._evidence_breeze_stench[
                (x, y)
            ] and self._has_surrounding_pits_wumpus(event, x, y):
                return 0
        return 1

    def _ask_probability_unsafe(self, x, y) -> float:
        vars = [
            probability.Variable(str((xf, yf)), [True, False])
            for (xf, yf) in self._fringe
            if (xf, yf) != (x, y)
        ]
        jpd = probability.JointDistribution()
        fringe_prob = 0
        evidence = {}
        evidence[(x, y)] = True
        for event in jpd.all_events(vars, evidence):
            print(event)
            prob = 1
            for (_, val) in event.items():
                if val:
                    prob *= 0.2
                else:
                    prob *= 0.8
            if self._consistent(event):
                fringe_prob += prob
        return prob

    def _get_safe_pos(self) -> Optional[Point]:
        risky_prob = 1
        next_pos = None
        for x, y in self._fringe:
            prob = self._ask_probability_unsafe(x, y)
            print((x, y), prob)
            if prob < risky_prob:
                risky_prob = prob
                next_pos = (x, y)
        return Point(*next_pos)

    def update(self):
        action = next(self._probabilistic_agent())
        pos = self.pos
        if action == Direction.UP:
            new_pos = Point(pos.x, pos.y - 1)
        elif action == Direction.DOWN:
            new_pos = Point(pos.x, pos.y + 1)
        elif action == Direction.LEFT:
            new_pos = Point(pos.x - 1, pos.y)
        else:
            new_pos = Point(pos.x + 1, pos.y)
        self._pos.update(new_pos)

    def __repr__(self) -> str:
        return f"HumanPlayer({self.pos}"


wumpus_world = create_wumpus_world()
p_agent = ProbabilisticAIPlayer(Point(0, 3), wumpus_world)
while True:
    p_agent.update()
    input()
