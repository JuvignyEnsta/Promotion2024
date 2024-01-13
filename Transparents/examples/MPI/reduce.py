import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

localSize = 5 # Taille locale pour chaque tableaux locaux (modifiable)
root      = 0  # Qui va recevoir le résultat final (modifiable)
op        = MPI.SUM # Le type de réduction (modifiable)

localValues = np.array([rank*localSize + i + 1 for i in range(localSize)], dtype=np.double)
result      = None
if rank == 0:
    result = np.empty(localSize, dtype=np.double)
# On effectue la réduction et on stocke le résultat dans result pour le processus root
globCom.Reduce([localValues,MPI.DOUBLE], [result,MPI.DOUBLE], op, root)

out.write(f"localValues : {localValues}\n")
if rank == 0:
    out.write(f"result of the reduction : {result}\n")

out.close()
