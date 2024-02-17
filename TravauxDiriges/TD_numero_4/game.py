import os

# Hide PyGame welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame

from grid import *

from time import time
from mpi4py import MPI

from patterns import patterns


# Initializes the communication
comm = MPI.COMM_WORLD.Dup()
nbp  = comm.size
rank = comm.rank


RESOLUTION_X = 800   # Pixels
RESOLUTION_Y = 800   # Pixels

# Indices for pack separation
interval = None


class App:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid

        # Number of cells in the grid
        self.size_x = RESOLUTION_X // self.grid.size[1]
        self.size_y = RESOLUTION_Y // self.grid.size[0]

        self.width = self.grid.size[1] * self.size_x
        self.height = self.grid.size[0] * self.size_y

        if rank != 0:
            return

        self.screen = pygame.display.set_mode((self.width, self.height))

        # Colors of the game
        self.life = pygame.Color("black")
        self.dead = pygame.Color("white")

        self.line = pygame.Color("lightgrey")

        # Draws horizontal lines once
        for i in range(self.grid.size[0]):
            pygame.draw.line(self.screen, self.line,
                (0, i * self.size_y), (self.width, i * self.size_y))

        # Draws vertical lines once
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
        if rank != 0:
            return

        # Draws only the changed cells
        for i, j in self.grid.diff:
            self.screen.fill(
                self.compute_color(i, j), self.compute_rectangle(i, j))

        pygame.display.update()


def parallel_update(app: App) -> None:
    global interval

    if interval is None:
        indices = np.array_split(np.arange(app.grid.size[0]), nbp)
        interval = (indices[rank][0], indices[rank][-1] + 1)

    # Updates the pack interval
    app.grid.update(*interval)

    cells = np.empty(app.grid.size, dtype=np.uint8)
    partial = app.grid.cells[interval[0]:interval[1]]

    # Joins the packages to complete the grid
    # Important: nbp must divides grid height
    comm.Allgather(partial, cells)
    app.grid.cells = cells

    # Sends the changed cells
    diff = comm.gather(app.grid.diff, root=0)

    if rank == 0:
        app.grid.diff = np.concatenate(diff, axis=0)


def main(choice: str = "glider") -> None:
    if rank == 0:
        pygame.init()

    grid = Grid(*patterns[choice])
    app = App(grid)

    running = app.height % nbp == 0

    if not running and rank == 0:
        print("Important: nbp must divides grid height")

    while running:
        start = time()
        parallel_update(app)
        elapsed = time() - start

        if rank == 0:
            print(f"Time to compute the next frame: {elapsed:2.2e} ", end="")

        start = time()
        app.draw()
        elapsed = time() - start

        if rank == 0:
            print(f"seconds, time to render: {elapsed:2.2e} seconds\r", end="")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        # Notifies game running status
        running = comm.scatter([running] * nbp, root=0)

    if rank == 0:
        pygame.quit()
        print()


if __name__ == "__main__":
    main(choice="acorn")
