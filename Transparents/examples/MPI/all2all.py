import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

localSize = 2*nbp # Taille locale pour chaque tableaux locaux (modifiable)

localValues = np.array([rank*localSize + i + 1 for i in range(localSize)], dtype=np.double)
result      = np.zeros(localSize, dtype=np.double)

# Store the reduction operation in result array
globCom.Alltoall([localValues, MPI.DOUBLE], [result,MPI.DOUBLE])

out.write(f"values before all2all : {localValues}\n")    
out.write(f"result after all2all : {result}\n")

out.close()
