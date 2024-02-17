import numpy as np

from typing import List, Tuple


class Grid:
    def __init__(self, size: Tuple[int, int], pattern: List[Tuple[int, int]] = None) -> None:
        self.size = size

        self.cells = np.zeros(self.size, dtype=np.uint8)

        if pattern is not None:
            i = [p[0] for p in pattern]
            j = [p[1] for p in pattern]
            self.cells[i, j] = 1

        self.diff = None

    def update(self) -> None:
        sy, sx = self.size

        copy = np.copy(self.cells)

        diff = []
        for i in range(sy):
            i_abv = (i - 1) % sy   # Cell above
            i_blw = (i + 1) % sy   # Cell below

            for j in range(sx):
                j_lef = (j - 1) % sx   # Cell to the left
                j_rig = (j + 1) % sx   # Cell to the right

                neighbors_i = [i_abv, i_abv, i_abv, i, i, i_blw, i_blw, i_blw]
                neighbors_j = [j_lef, j, j_rig, j_lef, j_rig, j_lef, j, j_rig]

                # All the 8 neighbors
                neighbors = self.cells[neighbors_i, neighbors_j]
                counter = np.sum(neighbors)

                # The cell is alive
                if self.cells[i,j] == 1:
                    if counter != 2 and counter != 3:
                        copy[i, j] = 0

                        if self.diff is not None:
                            diff.append((i, j))

                # The cell is dead
                elif counter == 3:
                    copy[i, j] = 1

                    if self.diff is not None:
                        diff.append((i, j))

                # Just to fix the visualization in the first frame
                if self.diff is None:
                    diff.append((i, j))

        self.diff = diff
        self.cells = copy
