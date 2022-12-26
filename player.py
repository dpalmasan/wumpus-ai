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


class Player(ABCMeta):
    @abstractmethod
    def update(self, direction=Direction) -> None:
        raise NotImplemented()

    @abstractmethod
    def draw(self) -> None:
        raise NotImplemented()


class LogicAIPlayer(Player):
    def __init__(self, pos: Point, kb: propositional.PropLogicKB) -> None:
        self._pos = pos
        self._kb = kb
        self._plan = []

    @property
    def pos(self) -> Point:
        return self._pos

    def _run_plan(self):
        for step in self._plan:
            yield step

    def update(self):

        direction = next(self._plan)
        if direction == Direction.UP:
            self._pos.update(self._pos.x, self._pos.y - 1)
        if direction == Direction.DOWN:
            self._pos.update(self._pos.x, self._pos.y + 1)
        if direction == Direction.LEFT:
            self._pos.update(self._pos.x - 1, self._pos.y)
        else:
            self._pos.update(self._pos.x + 1, self._pos.y)

    def draw(self, canvas, rect, color) -> None:
        pygame.draw.rect(canvas, color, rect, 1)
