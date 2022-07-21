from abc import ABC, abstractmethod
import sys
import pygame

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 400
WINDOW_WIDTH = 400

class Map:
    def __init__(self, block_size: int):
        self._block_size = block_size

    @property
    def block_size(self):
        return self._block_size

    def draw(self):
        blockSize = 50 #Set the size of the grid block
        for x in range(0, WINDOW_WIDTH, blockSize):
            for y in range(0, WINDOW_HEIGHT, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(SCREEN, BLACK, rect, 1)


class Tile(ABC):
    @abstractmethod
    def draw(self) -> None:
        raise NotImplemented()
    




def main():
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)

    while True:
        map = Map(50)
        map.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()




main()