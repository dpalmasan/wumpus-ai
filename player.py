from abc import abstractmethod
from enum import Enum
import pickle
import random
from typing import Optional
from pylogic.propositional import (
    Variable,
    CnfClause,
    DpllKB,
    ResolutionKB,
    pl_resolution,
    CnfParser,
    to_cnf,
)

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
        # self._kb.add(Variable(f"P{pos.x}{pos.y}", is_negated=True) & Variable(f"W{pos.x}{pos.y}", is_negated=True))
        self._kb.add(Variable(f"W{pos.x}{pos.y}", True))
        self._kb.add(Variable(f"P{pos.x}{pos.y}", True))
        self._breeze_stench_rules = wumpus_world._breeze_stench_rules()

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
        )

    def _pl_wumpus_agent(self) -> Direction:
        x, y = self.pos.x, self.pos.y
        self._perceive()
        self._visited[y][x] = True
        self._update_fringe()

        for row in self._visited:
            print(row)

        if "W" in self._wumpus_world[y][x] or "P" in self._wumpus_world[y][x]:
            raise Exception("YOU DIED!")
        elif "G" in self._wumpus_world[y][x]:
            raise Exception("YOU WON!")

        if len(self._plan):
            yield self._plan.pop(0)
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
        kb = DpllKB(self._kb.clauses.copy())
        p = Variable(f"P{i}{j}", is_negated=False, truthyness=None)
        for y in range(len(self._visited)):
            for x in range(len(self._visited[y])):
                if self._visited[y][x]:
                    for clause in self._breeze_stench_rules["B", Point(x, y)]:
                        kb.add(clause)
        for clause in self._breeze_stench_rules["B", Point(i, j)]:
            kb.add(clause)

        return kb.query(~p)

    def _check_if_no_wumpus(self, i, j) -> bool:
        kb = DpllKB(self._kb.clauses.copy())
        w = Variable(f"W{i}{j}", is_negated=False, truthyness=None)
        kb.add(self._wumpus_world._one_wumpus_rule())
        kb.add(wumpus_world._at_most_one_wumpus())
        for y in range(len(self._visited)):
            for x in range(len(self._visited[y])):
                if self._visited[y][x]:
                    for clause in self._breeze_stench_rules["S", Point(x, y)]:
                        kb.add(clause)
        for clause in self._breeze_stench_rules["S", Point(i, j)]:
            kb.add(clause)
        print(kb.clauses, kb.query(~w), i, j)
        return kb.query(~w)


    def _get_safe_pos(self) -> Optional[Point]:
        print(self._fringe)
        for i, j in self._fringe:
            input()
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

    def _is_valid_pos(self) -> True:
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


wumpus_world = create_wumpus_world()
ai_player = LogicAIPlayer(Point(0, 3), wumpus_world)
while True:
    ai_player.update()
