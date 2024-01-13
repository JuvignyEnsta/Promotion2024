import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

localSize = 5 # Taille locale pour chaque tableaux locaux (modifiable)
op        = MPI.SUM # Le type de réduction (modifiable)

localValues = np.array([rank*localSize + i + 1 for i in range(localSize)], dtype=np.double)
result      = np.zeros(localSize, dtype=np.double)
# On effectue la réduction et on stocke le résultat dans result pour tous les processus
globCom.Scan([localValues,MPI.DOUBLE], [result,MPI.DOUBLE], op)

out.write(f"localValues : {localValues}\n")    
out.write(f"result of the scan : {result}\n")

out.close()
