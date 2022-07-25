import sys
import pygame
from enum import Enum
from typing import Dict, Iterable, List, Tuple
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
X_TILE_COUNT = 4
Y_TILE_COUNT = 4
WINDOW_HEIGHT = BLOCK_SIZE * X_TILE_COUNT
WINDOW_WIDTH = BLOCK_SIZE * Y_TILE_COUNT
OFFSET = BLOCK_SIZE // 3
IMAGES_WIDTH = BLOCK_SIZE // 3
IMAGES_HEIGHT = BLOCK_SIZE // 3

breeze = pygame.transform.scale(
    pygame.image.load("breeze.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
stench = pygame.transform.scale(
    pygame.image.load("stench.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
wumpus = pygame.transform.scale(
    pygame.image.load("bear.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
gold = pygame.transform.scale(
    pygame.image.load("gold.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)

properties = [
    Property.BREEZE,
    Property.STENCH,
    Property.WUMPUS,
    Property.GOLD,
    Property.PIT,
]


class Tile:
    def __init__(
        self,
        pos: Position,
        properties: Iterable[Property] = [],
        size=(BLOCK_SIZE, BLOCK_SIZE),
    ):
        self._properties = properties
        self._size = size
        self._pos = pos
        self._surface = pygame.Surface(size)
        self._rect = pygame.Rect(pos.x, pos.y, *size)

    def draw(self, canvas: pygame.Surface) -> None:
        if Property.PIT in self._properties:
            pygame.draw.circle(canvas, BLACK, self._rect.center, BLOCK_SIZE // 3)

        if Property.BREEZE in self._properties:
            rect = breeze.get_rect()
            rect.center = (self._rect.center[0] - OFFSET, self._rect.center[1] - OFFSET)
            canvas.blit(breeze, rect)

        if Property.STENCH in self._properties:
            rect = stench.get_rect()
            rect.center = (self._rect.center[0], self._rect.center[1] - OFFSET)
            canvas.blit(stench, rect)

        if Property.WUMPUS in self._properties:
            rect = wumpus.get_rect()
            rect.center = (self._rect.center[0], self._rect.center[1])
            canvas.blit(wumpus, rect)

        if Property.GOLD in self._properties:
            rect = gold.get_rect()
            rect.center = (self._rect.center[0], self._rect.center[1] + OFFSET)
            canvas.blit(gold, rect)

        pygame.draw.rect(canvas, BLACK, self._rect, 1)


class Map:
    def __init__(self, tiles: Dict[Tuple[int, int], Tile]):
        self.tiles = tiles

    def draw(self, canvas: pygame.Surface):
        for _, tile in self.tiles.items():
            tile.draw(canvas)

    @classmethod
    def from_list(cls, grid: List[List[Iterable[Property]]]) -> "Map":
        tiles = {}
        #  For now we limit size to 6
        for j, x in zip(range(X_TILE_COUNT), range(0, WINDOW_WIDTH, BLOCK_SIZE)):
            for i, y in zip(range(Y_TILE_COUNT), range(0, WINDOW_HEIGHT, BLOCK_SIZE)):
                tiles[(x, y)] = Tile(Position(x, y), grid[i][j])

        return cls(tiles)


def main():
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)
    breeze.convert()

    tiles = [
        [(Property.STENCH,), [], (Property.BREEZE,), (Property.PIT,)],
        [
            (Property.WUMPUS,),
            (Property.BREEZE, Property.STENCH, Property.GOLD),
            (Property.PIT,),
            (Property.BREEZE,),
        ],
        [(Property.STENCH,), [], (Property.BREEZE,), []],
        [[], (Property.BREEZE,), (Property.PIT,), (Property.BREEZE,)],
    ]

    map = Map.from_list(tiles)
    while True:
        map.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


main()
