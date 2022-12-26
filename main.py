import sys
import pygame
from typing import Dict, Iterable, List, Tuple
from consts import (
    BLACK,
    BLOCK_SIZE,
    IMAGES_HEIGHT,
    IMAGES_WIDTH,
    OFFSET,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    X_TILE_COUNT,
    Y_TILE_COUNT,
    Property,
)
from utils import Position


breeze = pygame.transform.scale(
    pygame.image.load("assets/breeze.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
stench = pygame.transform.scale(
    pygame.image.load("assets/stench.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
wumpus = pygame.transform.scale(
    pygame.image.load("assets/bear.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)
gold = pygame.transform.scale(
    pygame.image.load("assets/gold.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
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
        self._tiles = tiles

    def draw(self, canvas: pygame.Surface):
        for _, tile in self._tiles.items():
            tile.draw(canvas)

    @classmethod
    def from_list(cls, grid: List[List[Iterable[Property]]]) -> "Map":
        tiles = {}
        #  For now we limit size to 6
        for j, x in zip(range(X_TILE_COUNT), range(0, WINDOW_WIDTH, BLOCK_SIZE)):
            for i, y in zip(range(Y_TILE_COUNT), range(0, WINDOW_HEIGHT, BLOCK_SIZE)):
                tiles[(x, y)] = Tile(Position(x, y), grid[i][j])

        return cls(tiles)

    def tile_state(self, x, y) -> Iterable[Property]:
        return self._tiles[(x, y)]


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
