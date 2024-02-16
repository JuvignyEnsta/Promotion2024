import numpy as np

from mpi4py import MPI


# Initializes the communication
comm = MPI.COMM_WORLD.Dup()
nbp  = comm.size
rank = comm.rank


dim = 1024

matrix = np.array(
    [[(i + j) % dim + 1.0 for i in range(dim)] for j in range(dim)]
)

vector = np.array([i + 1.0 for i in range(dim)])

# Block separation for each process
division = np.round(dim / nbp).astype(int)

# Indices for block separation
srt = rank * division
end = srt + division


def from_columns() -> None:
    result = np.empty(dim)

    partial = matrix[:, srt:end].dot(vector[srt:end])
    comm.Allreduce(partial, result, op=MPI.SUM)

    if rank == 0:
        print(result)


def from_rows() -> None:
    result = np.empty(dim)

    partial = matrix[srt:end].dot(vector)
    comm.Allgather(partial, result)

    if rank == 0:
        print(result)


if __name__ == "__main__":
    from_rows()
