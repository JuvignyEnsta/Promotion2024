import pygame

from grid import *

from time import time

from patterns import patterns


RESOLUTION_X = 800   # Pixels
RESOLUTION_Y = 800   # Pixels


class App:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid

        # Number of cells in the grid
        self.size_x = RESOLUTION_X // self.grid.size[1]
        self.size_y = RESOLUTION_Y // self.grid.size[0]

        self.width = self.grid.size[1] * self.size_x
        self.height = self.grid.size[0] * self.size_y

        self.screen = pygame.display.set_mode((self.width, self.height))

        # Colors of the game
        self.life = pygame.Color("black")
        self.dead = pygame.Color("white")

        self.line = pygame.Color("lightgrey")

        # Draw horizontal lines once
        for i in range(self.grid.size[0]):
            pygame.draw.line(self.screen, self.line,
                (0, i * self.size_y), (self.width, i * self.size_y))

        # Draw vertical lines once
        for j in range(self.grid.size[1]):
            pygame.draw.line(self.screen, self.line,
                (j * self.size_x, 0), (j * self.size_x, self.height))

    def compute_color(self, i: int, j: int) -> Tuple[int, int, int, int]:
        return self.dead if self.grid.cells[i, j] == 0 else self.life

    def compute_rectangle(self, i: int, j: int) -> Tuple[int, int, int, int]:
        pos_x = self.size_x * j
        pos_y = self.height - self.size_y * (i + 1)

        return (pos_x + 1, pos_y + 1, self.size_x - 1, self.size_y - 1)

    def draw(self) -> None:
        # Draw only the changed cells
        for i, j in self.grid.diff:
            self.screen.fill(
                self.compute_color(i, j), self.compute_rectangle(i, j))

        pygame.display.update()


def main(choice: str = "glider") -> None:
    pygame.init()

    grid = Grid(*patterns[choice])
    app = App(grid)

    while True:
        timer_1 = time()
        grid.update()
        timer_2 = time()
        app.draw()
        timer_3 = time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        print(f"Elapsed time to compute the next frame: {timer_2 - timer_1:2.2e} ", end="")
        print(f"seconds, elapsed time to render: {timer_3 - timer_2:2.2e} seconds\r", end="")


if __name__ == "__main__":
    main(choice="acorn")
