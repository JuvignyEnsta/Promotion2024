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

# Number of rows per pack
pack_size = 32

num_packs = height // pack_size


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
    partial = np.zeros((height, width), dtype=np.double)

    if rank == 0:
        result = np.empty((height, width), dtype=np.double)

        curr_pack = 0
        start = time()

        # Delegates the first task to each slave
        for process_index in range(1, nbp):
            comm.send(curr_pack, process_index)
            curr_pack += 1

        status = MPI.Status()

        # Distribute tasks to slaves as long as there are
        while curr_pack < num_packs:
            comm.recv(status=status)
            comm.send(curr_pack, dest=status.source)
            curr_pack += 1

        for process_index in range(1, nbp):
            comm.recv(status=status)

            # Sends -1 to indicate that tasks are finished
            comm.send(-1, dest=status.source)

        comm.Reduce(partial, result, op=MPI.SUM, root=0)
        elapsed = time() - start

        print(f"Elapsed time to compute the Mandelbrot set: {elapsed}")

        start = time()
        image = Image.fromarray(np.uint8(255 * plasma(result)))
        elapsed = time() - start

        print(f"Elapsed time to generate the image: {elapsed}")
        image.show()

    else:
        mandelbrot = Mandelbrot(escape_radius=10, max_iterations=50)

        status = MPI.Status()
        curr_pack = comm.recv(source=0)

        while curr_pack != -1:
            # print(f"Rank {rank} -> task {curr_pack + 1}/{num_packs}")

            for t in range(pack_size):
                for x in range(width):
                    y = t + curr_pack * pack_size
                    c = complex(-2.0 + scale_x * x, -1.125 + scale_y * y)
                    partial[y, x] = mandelbrot.convergence(c, smooth=True)

            request = comm.isend(1, 0)
            curr_pack = comm.recv(source=0)
            request.wait()

        comm.Reduce(partial, None, op=MPI.SUM, root=0)


if __name__ == "__main__":
    parallel_image()
