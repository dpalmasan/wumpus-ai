from abc import ABCMeta, abstractmethod
from enum import Enum
from pylogic import propositional

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from utils import Point


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


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
    def __init__(self, pos: Point, kb: propositional.PropLogicKB) -> None:
        self._kb = kb
        self._plan = []

    def _run_plan(self):
        for step in self._plan:
            yield step

    def update(self, new_pos: Point):

        direction = next(self._plan)
        self._pos.update(new_pos)

class HumanPlayer(Player):
    def __init__(self, pos):
        Player.__init__(self, pos)

    def update(self, new_pos):
        self._pos = new_pos

    def __repr__(self) -> str:
        return f"HumanPlayer({self.pos}"
