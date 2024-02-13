import numpy as np

from mpi4py import MPI
from mpi4py.util.dtlib import from_numpy_dtype, to_numpy_dtype


def pprint(*args, **kwargs):
    print(f"[{rank:02d}]", *args, **kwargs)

def zprint(*args, **kwargs):
    if rank == 0:
        pprint(*args, **kwargs)
    
comm = MPI.COMM_WORLD.Dup()
nbp = comm.size
rank = comm.rank

random_sizes = [0, 3, 2, 5, 12, 3, 8, 7]
if nbp > len(random_sizes):
    raise RuntimeError("This program only works with <=%d processes."%len(random_sizes))

loc_array = np.ones(shape=(random_sizes[rank],), dtype=np.int32) * rank
pprint("My local array:", loc_array)

# process 0 needs to know all local sizes for gatherv:
loc_sizes = comm.gather(len(loc_array), root=0)
zprint("local sizes:", loc_sizes)

if rank == 0:
    glob_array = np.zeros(shape=(sum(loc_sizes),), dtype=np.int32)
else:
    glob_array = None

    
# Detailed call to Gatherv:
comm.Gatherv([loc_array, len(loc_array), MPI.INT32_T], # source buffer, local size, type
             [glob_array, loc_sizes, MPI.INT32_T],     # dest buffer, all local sizes, type
             root=0)
zprint("The global gathered array (1):", glob_array)

# Shorter call (type is deduced from the np array):
if rank == 0: glob_array *= 0
comm.Gatherv(loc_array,   # source buffer
             [glob_array, loc_sizes], # dest buffer and local sizes, the rest is deduced
             root=0)
zprint("The global gathered array (2):", glob_array)

# Shuffled storage in destination:
displacements = [0, 5, 8, 0]
if rank == 0: glob_array *= 0
comm.Gatherv(loc_array,   # source buffer
             [glob_array, loc_sizes, displacements, MPI.INT32_T], # dest buffer, local sizes, offsets (and type to avoid confusion)
             root=0)
zprint("The global gathered array (shuffled):", glob_array)
