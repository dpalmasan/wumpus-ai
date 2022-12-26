from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pylogic import propositional


class Point:
    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def x(self) -> int:
        return self._y

    def update(self, x_new: int, y_new: int) -> None:
        self._x = x_new
        self._y = y_new

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


class Player(ABCMeta):
    @abstractmethod
    def update(self) -> None:
        raise NotImplemented()


class LogicAIPlayer(Player):
    def __init__(self, initial_pos: Point, kb: propositional.PropLogicKB) -> None:
        self._pos = initial_pos
        self._kb = kb

    def update(self):
        raise NotImplemented()
