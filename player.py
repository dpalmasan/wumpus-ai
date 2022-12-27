from abc import abstractmethod
from enum import Enum
import random
from pylogic.propositional import (
    Variable,
    CnfClause,
    PropLogicKB,
    pl_resolution,
)

import os

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
    def __init__(self, pos: Point, kb: PropLogicKB) -> None:
        Player.__init__(self, pos)
        self._kb = kb
        self._plan = []
        self._safe_coords = set()

    def _find_safe_spot(self) -> Point:
        for x, y in self._safe_coords:
            not_wumpus = Variable(f"W{x}{y}", False)
            not_pit = Variable(f"P{x}{y}", False)
            alpha = not_wumpus & not_pit

            if pl_resolution(self._kb, alpha):
                return Point(x, y)

        raise NoAvailableSafeTiles("No available safe coord was found.")

    def _random_move(self, visited) -> Direction:
        possible_moves = []
        if self.pos.x > 0:
            possible_moves.append(Direction.LEFT)

        if self.pos.x < len(visited[0]) - 1:
            possible_moves.append(Direction.RIGHT)

        if self.pos.y < len(visited) - 1:
            possible_moves.append(Direction.UP)

        if self.pos.y > 0:
            possible_moves.append(Direction.DOWN)

        return random.choice(possible_moves)

    def _pl_wumpus_agent(self, visited, wumpus_world, x, y):
        for step in self._plan:
            yield step
        visited[y][x] = True
        self._perceive(wumpus_world, x, y)
        try:
            goal_coord = self._find_safe_spot()
            route_problem = ShortestPathSearchProblem(Point(x, y), goal_coord, visited)
            plan = a_star_route(route_problem, manhattan_heuristic)
            for action in plan:
                if action == "up":
                    action_enum = Direction.UP
                elif action == "down":
                    action_enum = Direction.DOWN
                elif action == "left":
                    action_enum = Direction.LEFT
                else:
                    action_enum = Direction.RIGHT
                yield action_enum
        except NoAvailableSafeTiles:
            yield self._random_move(x, y)

    def update(self, new_pos: Point):

        action = next(self._pl_wumpus_agent)
        if action == Direction.UP:
            new_pos = Point(self.x, self.y - 1)
        elif action == Direction.DOWN:
            new_pos = Point(self.x, self.y + 1)
        elif action == Direction.LEFT:
            new_pos = Point(self.x - 1, self.y)
        else:
            new_pos = Point(self.x + 1, self.y)
        self._pos.update(new_pos)

    def _perceive(self, wumpus_world, x, y):
        if ("S" in wumpus_world[y][x]):
            clause = CnfClause([Variable(f"S{x}{y}")])
        else:
            clause = CnfClause([Variable(f"S{x}{y}", False)])

        self._kb.add(clause)

        if ("B" in wumpus_world):
            clause = CnfClause([Variable(f"B{x}{y}")])
        else:
            clause = CnfClause([Variable(f"B{x}{y}", False)])

        self._kb.add(clause)

        

class HumanPlayer(Player):
    def __init__(self, pos):
        Player.__init__(self, pos)

    def update(self, new_pos):
        self._pos = new_pos

    def __repr__(self) -> str:
        return f"HumanPlayer({self.pos}"
