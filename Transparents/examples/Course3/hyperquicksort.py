import numpy as np
import time
from mpi4py import MPI
import sys
from math import sqrt, log2

out  = None
DEBUG= 0

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

N = 256_000

if len(sys.argv) > 1:
    N = int(sys.argv[1])

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

reste= N % nbp
assert(reste == 0)
NLoc = N//nbp
out.write(f"Nombre de valeurs locales : {NLoc}`\n")

# Génération du tableau local de valeurs
values = np.random.randint(-32768, 32768, size=NLoc,dtype=np.int64)
out.write(f"Valeurs initiales : {values}\n")

# Calcul de la dimension de l'hypercube
dim = int(log2(nbp)+0.1)
if (1<<dim) != nbp :
    print("Le nombre de processeur doit être une puissance de deux !")
    globCom.Abort(-1)
out.write(f"Dimension du cube : {dim}\n")


debut = time.time()
status = MPI.Status()
buffer = None
values.sort()
for d in range(dim-1,-1,-1):
    if DEBUG: out.write(f"Dimension {d}\n")
    subCube = globCom.Split(rank//(1<<(d+1)), rank)
    srank = subCube.rank
    pivot : int = 0
    if srank == 0:  
        pivot = values[len(values)//2-1]
        if DEBUG: out.write(f"\tPivot a envoyé : {pivot}\n"); out.flush()
    pivot = subCube.bcast(pivot, 0)
    if DEBUG: out.write(f"\tPivot récupéré : {pivot}\n"); out.flush()
    # Partage le tableau en deux parties axées autour du pivot :
    lowBound = values <= pivot # Masque pour les valeurs plus petites ou égales au pivot
    highBound= values >  pivot # Masque pour les valeurs plus grandes que le pivot
    lowValues = values[lowBound]
    highValues = values[highBound]
    if DEBUG: out.write(f"\tlowValues = {lowValues}\n"); out.flush()
    if DEBUG: out.write(f"\tHigh Values = {highValues}\n"); out.flush()

    if (rank & (1<<d)) == 0:
        if DEBUG: out.write(f"\tPairing avec {rank+ (1<<d)}.Send\n"); out.flush()
        globCom.Ssend([highValues,MPI.INT64_T], dest=rank + (1<<d))
        globCom.Probe(source=rank + (1<<d), status=status)
        recvSize = status.Get_count()//8
        buffer = np.empty(recvSize, dtype=np.int64)
        if DEBUG: out.write(f"\tPairing avec {rank+ (1<<d)}.Recv\n"); out.flush()
        globCom.Recv([buffer, MPI.INT64_T], source=rank + (1<<d))
        if DEBUG: out.write(f"\tFusion sort between {lowValues} and buffer {buffer}\n"); out.flush()
        values = np.concatenate((buffer, lowValues))
        values.sort(kind="mergesort")
    else:
        if DEBUG: out.write(f"\tPairing avec {rank-(1<<d)}.Recv.\n"); out.flush()
        globCom.Probe(source=rank - (1<<d), status = status)
        recvSize = status.Get_count()//8
        buffer = np.empty(recvSize, dtype=np.int64)
        globCom.Recv([buffer,MPI.INT64_T], source=rank-(1<<d))
        if DEBUG: out.write(f"\tPairing avec {rank-(1<<d)}.Send.\n"); out.flush()
        globCom.Ssend([lowValues, MPI.INT64_T],  dest=rank-(1<<d))
        if DEBUG: out.write(f"\tFusion sort between {highValues} and buffer {buffer}\n"); out.flush()
        values = np.concatenate((buffer, highValues))
        values.sort(kind="mergesort")
    if DEBUG :
        out.write(f"\tValues : {values}\n"); out.flush()
fin = time.time()
out.write(f"Temps local pour le tri : {fin-debut} secondes\n")
if values.shape[0] > 0:
    out.write(f"Première valeurs locale : {values[0]}\n")
    out.write(f"Dernière valeurs locale : {values[-1]}\n")
    out.write(f"values : {values}\n")

out.close()
