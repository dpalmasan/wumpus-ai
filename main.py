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
BLOCK_SIZE = 128
WINDOW_HEIGHT = BLOCK_SIZE * 6
WINDOW_WIDTH = BLOCK_SIZE * 6
OFFSET = BLOCK_SIZE // 3
IMAGES_WIDTH = BLOCK_SIZE // 3
IMAGES_HEIGHT = BLOCK_SIZE // 3

breeze = pygame.transform.scale(pygame.image.load("breeze.png"), (IMAGES_WIDTH, IMAGES_HEIGHT))
stench = pygame.transform.scale(pygame.image.load("stench.png"), (IMAGES_WIDTH, IMAGES_HEIGHT))

properties = [Property.BREEZE, Property.STENCH]


class Map:
    def __init__(self, block_size: int):
        self._block_size = block_size

    @property
    def block_size(self):
        return self._block_size

    def draw(self, canvas: pygame.Surface):
        for x in range(0, WINDOW_WIDTH, self.block_size):
            for y in range(0, WINDOW_HEIGHT, self.block_size):
                tile = Tile(Position(x, y), properties)
                tile.draw(canvas)


class Tile:
    def __init__(self, pos: Position, properties: List[Property] = [], size=(BLOCK_SIZE, BLOCK_SIZE)):
        self._properties = properties
        self._size = size
        self._pos = pos
        self._surface = pygame.Surface(size)
        self._rect = pygame.Rect(pos.x, pos.y, *size)

    def draw(self, canvas: pygame.Surface) -> None:
        if Property.BREEZE in self._properties:
            rect = breeze.get_rect()
            rect.center = (self._rect.center[0] - OFFSET, self._rect.center[1] - OFFSET)
            canvas.blit(breeze, rect)

        if Property.STENCH in self._properties:
            rect = stench.get_rect()
            rect.center = (self._rect.center[0], self._rect.center[1] - OFFSET)
            canvas.blit(stench, rect)
        
        pygame.draw.rect(canvas, BLACK, self._rect, 1)


def main():
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)
    breeze.convert()

    while True:
        map = Map(BLOCK_SIZE)
        map.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

main()
