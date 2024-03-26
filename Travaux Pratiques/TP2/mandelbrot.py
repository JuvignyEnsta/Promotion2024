import numpy as np

from PIL import Image
from time import time

from mpi4py import MPI

from typing import Union

from matplotlib.cm import plasma


# Initializes the communication
comm = MPI.COMM_WORLD.Dup()
nbp  = comm.size
rank = comm.rank


width, height = 1024, 1024

scale_x = 3.00 / width
scale_y = 2.25 / height

# Pack separation for each process
division = np.round(height / nbp).astype(int)

# Indices for pack separation
srt = rank * division
end = srt + division


class Mandelbrot:
    def __init__(self, escape_radius: float, max_iterations: int) -> None:
        self.escape_radius = escape_radius
        self.max_iterations = max_iterations

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth: bool = False) -> float:
        return self.count_iterations(c, smooth) / self.max_iterations

    def count_iterations(self, c: complex, smooth: bool) -> Union[int, float]:
        # We check whether the complex number
        # belongs to a known convergence zone:

        # 1. Belonging to the disk C0{(0, 0), 1/4}
        if c.real * c.real + c.imag * c.imag < 0.0625:
            return self.max_iterations

        # 2. Belonging to the disk C1{(-1, 0), 1/4}
        if (c.real + 1) * (c.real + 1) + c.imag * c.imag < 0.0625:
            return self.max_iterations

        # 3.  Belonging to the cardioid {(1/4, 0), 1/2 (1 - cos(theta))}
        if -0.75 < c.real and c.real < 0.5:
            norm = abs(c - 0.25)

            if norm < 0.5 * (1.25 - c.real / max(norm, 1.0e-14)):
                return self.max_iterations

        z = 0.0

        for iter in range(self.max_iterations):
            z = z**2 + c
            norm = abs(z)

            if norm > self.escape_radius:
                return iter + 1.0 - np.log2(np.log(norm)) if smooth else iter

        return self.max_iterations


def parallel_image() -> None:
    mandelbrot = Mandelbrot(escape_radius=10, max_iterations=50)

    result = np.empty((height, width), dtype=np.double)
    partial = np.empty((division, width), dtype=np.double)

    start = time()
    for y in range(srt, end):
        for x in range(width):
            c = complex(-2.0 + scale_x * x, -1.125 + scale_y * y)
            partial[y - srt, x] = mandelbrot.convergence(c, smooth=True)

    comm.Gather(partial, result, root=0)
    elapsed = time() - start

    if rank == 0:
        print(f"Elapsed time to compute the Mandelbrot set: {elapsed}")

        start = time()
        image = Image.fromarray(np.uint8(255 * plasma(result)))
        elapsed = time() - start

        print(f"Elapsed time to generate the image: {elapsed}")
        image.show()


if __name__ == "__main__":
    parallel_image()
