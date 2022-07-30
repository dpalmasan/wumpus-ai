from abc import ABCMeta, abstractmethod
from pylogic import propositional

class Player(ABCMeta):
    @abstractmethod
    def update(self):
        raise NotImplemented()



class LogicAIPlayer(Player):
    def __init__(self, kb: propositional.PropLogicKB):
        self._kb = kb

    def update(self):
        return None