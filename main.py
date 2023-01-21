import sys
import time
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
from player import HumanPlayer, LogicAIPlayer, ProbabilisticAIPlayer
from wumpus import WumpusWorld, create_wumpus_world, create_wumpus_world2


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


class Pane(object):
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 25)

    def add_rect(self, canvas):
        self.rect = pygame.draw.rect(
            canvas, BLACK, (WINDOW_WIDTH // 2, 75, 200, 100), 2
        )
        self.rect = pygame.draw.rect(
            canvas,
            WHITE,
            (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 2 * OFFSET, 200, BLOCK_SIZE),
        )

    def add_text(self, canvas, text="hello"):
        canvas.blit(
            self.font.render(text, True, (255, 0, 0)),
            (
                WINDOW_WIDTH // 2 - OFFSET,
                WINDOW_HEIGHT // 2 - OFFSET,
            ),
        )


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


def draw_visible_cells(canvas, seen):
    for j in range(len(seen)):
        for i in range(len(seen[0])):
            if not seen[i][j]:
                rect = pygame.Rect(
                    j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE
                )
                pygame.draw.rect(canvas, BLACK, rect)


def process_human_input(event, pos, agent, tiles: WumpusWorld):
    if event.type == pygame.KEYDOWN:
        updated = False
        if event.key == pygame.K_DOWN:
            new_pos = Point(pos.x, min(pos.y + 1, len(tiles._grid) - 1))
            updated = True
        elif event.key == pygame.K_UP:
            new_pos = Point(pos.x, max(pos.y - 1, 0))
            updated = True
        elif event.key == pygame.K_LEFT:
            new_pos = Point(max(pos.x - 1, 0), pos.y)
            updated = True
        elif event.key == pygame.K_RIGHT:
            new_pos = Point(min(pos.x + 1, len(tiles._grid) - 1), pos.y)
            updated = True
        if updated:
            agent.update(new_pos)


def main():
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    SCREEN.fill(WHITE)
    breeze.convert()

    current_pos = Point(0, 3)
    seen = []
    for j in range(4):
        row = []
        for i in range(4):
            if Point(i, j) == current_pos:
                row.append(True)
            else:
                row.append(False)
        seen.append(row)
    wumpus_world = create_wumpus_world2()
    agent = HumanPlayer(current_pos)
    agent = LogicAIPlayer(current_pos, wumpus_world, seen)
    agent = ProbabilisticAIPlayer(current_pos, wumpus_world)

    map = Map.from_list(wumpus_world)
    rect = player.get_rect()
    rect.center = (
        rect.center[0] + OFFSET + agent.pos.x * BLOCK_SIZE,
        rect.center[1] + OFFSET + agent.pos.y * BLOCK_SIZE,
    )
    SCREEN.blit(player, rect)
    draw_background(SCREEN, map.get_tiles_coords())
    Pan3 = Pane()

    while True:

        if (
            Property.GOLD in wumpus_world[agent.pos.y][agent.pos.x]
            or Property.PIT in wumpus_world[agent.pos.y][agent.pos.x]
            or Property.WUMPUS in wumpus_world[agent.pos.y][agent.pos.x]
        ):
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            pos = agent.pos
            if isinstance(agent, HumanPlayer):
                process_human_input(event, pos, agent, wumpus_world)
            else:
                if event.type == pygame.KEYDOWN:
                    agent.update()
                    seen[agent.pos.y][agent.pos.x] = True
                    time.sleep(1)

        new_pos = agent.pos
        if current_pos != agent.pos:
            seen[new_pos.y][new_pos.x] = True
            if wumpus_world[current_pos.y][current_pos.x]:
                wumpus_world[current_pos.y][current_pos.x].remove(Property.PLAYER)

            wumpus_world[new_pos.y][new_pos.x].add(Property.PLAYER)

        SCREEN.fill(WHITE)
        rect = player.get_rect()
        position = rect.move(
            OFFSET + agent.pos.x * BLOCK_SIZE, OFFSET + agent.pos.y * BLOCK_SIZE
        )
        SCREEN.blit(player, position)
        map.draw(SCREEN)
        draw_visible_cells(SCREEN, seen)
        draw_background(SCREEN, map.get_tiles_coords())
        pygame.display.update()

        clock.tick(60)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                waiting = False

        SCREEN.fill(WHITE)
        rect = player.get_rect()
        position = rect.move(
            OFFSET + agent.pos.x * BLOCK_SIZE, OFFSET + agent.pos.y * BLOCK_SIZE
        )
        SCREEN.blit(player, position)
        map.draw(SCREEN)
        draw_visible_cells(SCREEN, seen)
        draw_background(SCREEN, map.get_tiles_coords())
        Pan3.add_rect(SCREEN)
        if Property.GOLD in wumpus_world[agent.pos.y][agent.pos.x]:
            Pan3.add_text(SCREEN, "You won")
        else:
            Pan3.add_text(SCREEN, "You lost")
        pygame.display.update()


main()
