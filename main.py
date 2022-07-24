from abc import ABC, abstractmethod
import sys
import pygame
from enum import Enum
from typing import List
from dataclasses import dataclass

class Property(Enum):
    BREEZE = 0
    STENCH = 1
    GOLD = 2
    PIT = 3
    WUMPUS = 4

@dataclass
class Position:
    x: int
    y: int

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 64*6
WINDOW_WIDTH = 64*6

breeze = pygame.transform.scale(pygame.image.load('breeze.png'), (21, 21))

class Map:
    def __init__(self, block_size: int):
        self._block_size = block_size

    @property
    def block_size(self):
        return self._block_size

    def draw(self):
        blockSize = 64
        for x in range(0, WINDOW_WIDTH, blockSize):
            for y in range(0, WINDOW_HEIGHT, blockSize):
                tile = Tile(Position(x, y))
                tile.draw(SCREEN)


class Tile:
    def __init__(self, pos: Position, properties: List[Property] = [] , size =(64, 64)):
        self._properties = properties
        self._size = size
        self._pos = pos
        self._surface = pygame.Surface(size)
        self._rect = pygame.Rect(pos.x, pos.y, *size)


    def draw(self, canvas: pygame.Surface) -> None:
        canvas.blit(breeze, self._rect)
        pygame.draw.rect(canvas, BLACK, self._rect, 1)


def main():
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)
    breeze.convert()

    while True:
        map = Map(50)
        map.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()




main()