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
from utils import Point
from player import HumanPlayer


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

player = pygame.transform.scale(
    pygame.image.load("assets/player.png"), (IMAGES_WIDTH, IMAGES_HEIGHT)
)

properties = [
    Property.BREEZE,
    Property.STENCH,
    Property.WUMPUS,
    Property.GOLD,
    Property.PIT,
    Property.PLAYER,
]


class Tile:
    def __init__(
        self,
        pos: Point,
        properties: Iterable[Property] = [],
        size=(BLOCK_SIZE, BLOCK_SIZE),
    ):
        self._properties = properties
        self._size = size
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


class Map:
    def __init__(self, tiles: Dict[Tuple[int, int], Tile]):
        self._tiles = tiles

    def draw(self, canvas: pygame.Surface):
        for _, tile in self._tiles.items():
            tile.draw(canvas)

    def get_tiles_coords(self):
        return self._tiles.keys()

    @classmethod
    def from_list(cls, grid: List[List[Iterable[Property]]]) -> "Map":
        tiles = {}
        #  For now we limit size to 6
        for j, x in zip(range(X_TILE_COUNT), range(0, WINDOW_WIDTH, BLOCK_SIZE)):
            for i, y in zip(range(Y_TILE_COUNT), range(0, WINDOW_HEIGHT, BLOCK_SIZE)):
                tiles[(x, y)] = Tile(Point(x, y), grid[i][j])

        return cls(tiles)

    def tile_state(self, x, y) -> Iterable[Property]:
        return self._tiles[(x, y)]

def draw_background(canvas, tiles_coords):
    for x, y in tiles_coords:
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(canvas, BLACK, rect, 1)

def main():
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    SCREEN.fill(WHITE)
    breeze.convert()

    current_pos = Point(0, 3)
    agent = HumanPlayer(current_pos)
    tiles = [
        [[Property.STENCH], [], [Property.BREEZE], [Property.PIT,]],
        [
            [Property.WUMPUS],
            [Property.BREEZE, Property.STENCH, Property.GOLD],
            [Property.PIT],
            [Property.BREEZE],
        ],
        [[Property.STENCH], [], [Property.BREEZE], []],
        [[Property.PLAYER], [Property.BREEZE], [Property.PIT], [Property.BREEZE]],
    ]

    map = Map.from_list(tiles)
    rect = player.get_rect()
    rect.center = (rect.center[0] + OFFSET + agent.pos.x * BLOCK_SIZE, rect.center[1] + OFFSET + agent.pos.y * BLOCK_SIZE)
    SCREEN.blit(player, rect)
    draw_background(SCREEN, map.get_tiles_coords())
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            pos = agent.pos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    new_pos = Point(pos.x, pos.y + 1)
                if event.key == pygame.K_UP:
                    new_pos = Point(pos.x, pos.y - 1)
                if event.key == pygame.K_LEFT:
                    new_pos = Point(pos.x - 1, pos.y)
                if event.key == pygame.K_RIGHT:
                    new_pos = Point(pos.x + 1, pos.y)
                agent.update(new_pos)

        new_pos = agent.pos
        if current_pos != agent.pos:
            if tiles[current_pos.y][current_pos.x]:
                tiles[current_pos.y][current_pos.x].pop()

            tiles[new_pos.y][new_pos.x].append(Property.PLAYER)
            
        SCREEN.fill(WHITE)
        rect = player.get_rect()
        position = rect.move(OFFSET + agent.pos.x * BLOCK_SIZE, OFFSET + agent.pos.y * BLOCK_SIZE)
        SCREEN.blit(player, position)
        map.draw(SCREEN)
        draw_background(SCREEN, map.get_tiles_coords())
        pygame.display.update()
        clock.tick(60)



main()
