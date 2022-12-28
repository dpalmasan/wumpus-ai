from abc import abstractmethod
from enum import Enum
import pickle
import random
from pylogic.propositional import (
    Variable,
    CnfClause,
    PropLogicKB,
    pl_resolution,
    CnfParser,
    to_cnf,
)

import os

from wumpus import WumpusWorld

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
    def __init__(self, pos: Point, wumpus_world: WumpusWorld) -> None:
        Player.__init__(self,
            pos,
        )
        self._pos = pos

    def update(self):

        action = Direction.UP
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
