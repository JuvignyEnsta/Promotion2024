import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

root = 0 # Qui a le tableau au départ (peut être modifié)

values = None
if rank==root:
    values = np.array([2,3,5,7,11,13], dtype=np.int32)
else:
    values = np.empty(6, dtype=np.int32)

globCom.Bcast([values, MPI.INT32_T],root)

out.write(f"values : {values}\n")    

out.close()
