import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

globalSize = 101 # Taille globale du tableau initial (modifiable)

# Calcul de la taille locale du tableau reçu pour le processus courant :
localSize  = globalSize//nbp
if rank < globalSize%nbp:
    localSize += 1

root      = 0 # Qui détient le tableau initial (modifiable)

scatteredData = np.empty(localSize, dtype=np.int64)
globalData    = None
if rank==root:
    globalData = np.array([6*i-1 for i in range(globalSize)], dtype=np.int64)

globCom.Scatterv([globalData,MPI.INT64_T], [scatteredData,MPI.INT64_T], root)

out.write(f"Scattered data : {scatteredData}\n")    

out.close()
