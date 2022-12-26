from abc import ABCMeta, abstractmethod
from enum import Enum
from pylogic import propositional

from utils import Point


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Player(ABCMeta):
    @abstractmethod
    def update(self) -> None:
        raise NotImplemented()


class LogicAIPlayer(Player):
    def __init__(self, pos: Point, kb: propositional.PropLogicKB) -> None:
        self._pos = pos
        self._kb = kb
        self._plan = []

    @property
    def pos(self) -> Point:
        return self._pos

    def update(self, direction: Direction):
        if direction == Direction.UP:
            self._pos.update(self._pos.x, self._pos.y - 1)
        if direction == Direction.DOWN:
            self._pos.update(self._pos.x, self._pos.y + 1)
        if direction == Direction.LEFT:
            self._pos.update(self._pos.x - 1, self._pos.y)
        else:
            self._pos.update(self._pos.x + 1, self._pos.y)

        def draw(self) -> None:


