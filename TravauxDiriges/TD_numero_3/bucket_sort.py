import numpy as np

from time import time

from mpi4py import MPI


# Initializes the communication
comm = MPI.COMM_WORLD.Dup()
nbp  = comm.size
rank = comm.rank


dim = 10_000_000


def bucket_sort(debug: bool = False) -> None:
    vector = np.empty(dim)

    if rank == 0:
        # Computes the random vector
        vector = np.random.uniform(0.0, 1.0, dim)

    start = time()

    # Scatters the vector between the processors to calculate the min & max
    partial = comm.scatter(np.array_split(vector, nbp), root=0)

    min_value = comm.allreduce(np.min(partial), op=MPI.MIN)
    max_value = comm.allreduce(np.max(partial), op=MPI.MAX)

    convert = nbp / (max_value - min_value)

    # Calculates the bucket index for each value
    indices = np.floor(convert * (partial - min_value)).astype(int)

    # Fixes the maximum value in the last bucket
    indices[indices == nbp] = nbp - 1

    buckets = [partial[indices == index] for index in range(nbp)]

    bucket = np.concatenate(comm.alltoall(buckets))
    bucket.sort()

    if debug:
        print(f"Rank {rank}: {len(bucket)}/{dim} elements")

    result = comm.gather(bucket, root=0)

    if rank == 0:
        result = np.concatenate(result)

        elapsed = time() - start
        print(f"Elapsed time to sort the vector: {elapsed}")


if __name__ == "__main__":
    bucket_sort()
