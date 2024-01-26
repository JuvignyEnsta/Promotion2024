import numpy as np
import time
from mpi4py import MPI
import sys
from math import sqrt, log2

commCubes = []
out       = None

def sortBitonicSequence( bitonicSequence, increasingSort : bool = True ):
    nbLocalVals = bitonicSequence.shape[0]
    if nbLocalVals==1 : return bitonicSequence
    if nbLocalVals==2:
        if increasingSort:
            if bitonicSequence[0] > bitonicSequence[1]:  bitonicSequence[0] , bitonicSequence[1] = bitonicSequence[1] , bitonicSequence[0]
        else:
            if bitonicSequence[0] < bitonicSequence[1]:  bitonicSequence[0] , bitonicSequence[1] = bitonicSequence[1] , bitonicSequence[0]
        return bitonicSequence
    Nd2 : int = nbLocalVals//2
    if increasingSort:
        for i in range(Nd2):
            if bitonicSequence[i] > bitonicSequence[Nd2+i] : bitonicSequence[i], bitonicSequence[Nd2+i] = bitonicSequence[Nd2+i], bitonicSequence[i]
    else:
        for i in range(Nd2):
            if bitonicSequence[i] < bitonicSequence[Nd2+i] : bitonicSequence[i], bitonicSequence[Nd2+i] = bitonicSequence[Nd2+i], bitonicSequence[i]
    bitonicSequence[:Nd2] = sortBitonicSequence(bitonicSequence[:Nd2], increasingSort)
    bitonicSequence[Nd2:] = sortBitonicSequence(bitonicSequence[Nd2:], increasingSort)
    return bitonicSequence
# ====================================================================================================================
def distributedSortBitonicSequence( bitonicSequence, level: int, increasingSort : bool = True ):
    comm : MPI.Comm = commCubes[level]
    rank = comm.rank
    nbp  = comm.size

    exchgRank = rank + nbp//2 if 2*rank < nbp else rank - nbp//2

    status = MPI.Status()
    buffer = np.empty(bitonicSequence.shape[0], dtype=np.int64)

    comm.Sendrecv(bitonicSequence, exchgRank, 303, buffer, exchgRank, 303, status)

    if 2*rank < nbp:
        if increasingSort:
            bitonicSequence[:] = np.minimum(bitonicSequence, buffer)
        else:
            bitonicSequence[:] = np.maximum(bitonicSequence, buffer)
    else:
        if increasingSort:
            bitonicSequence[:] = np.maximum(bitonicSequence, buffer)
        else:
            bitonicSequence[:] = np.minimum(bitonicSequence, buffer)
 
    if level > 1:
        distributedSortBitonicSequence( bitonicSequence, level-1, increasingSort)
    else: 
        sortBitonicSequence( bitonicSequence, increasingSort)
# ====================================================================================================================

N = 65_536

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

reste = N%nbp
NLoc  = N//nbp
if reste != 0:
    print("Le nombre de processeur doit diviser le nombre d'éléments à trier.")
    globCom.Abort(-1)

# Génération du tableau local de valeurs
values = np.random.randint(-32768, 32768, size=NLoc,dtype=np.int64)
out.write(f"Valeurs initiales : {values}\n")

# Calcul la dimension de l'hypercube :
dim = int(log2(nbp)+0.1)
if (1<<dim) != nbp :
    print("Le nombre de processeur doit être une puissance de deux !")
    globCom.Abort(-1)
out.write(f"Dimension du cube : {dim}\n")

status = MPI.Status()
debut = time.time()
commCubes.append(None)
for idim in range(1, dim):
    commCubes.append(globCom.Split(rank//(1<<idim), rank))
commCubes.append(globCom.Dup())
if rank%2 == 0: # Pair : on trie dans l'ordre croissant
    values.sort()
else: # Impair, on trie dans l'ordre décroissant
    values.sort()
    values[:] = np.flip(values)
for d in range(dim):
    # out.write(f"Avant itération {d} : {values}\n")
    # Si rank%(2^(d+2)) < 2^{d+1} => increasing sinon decreasing
    distributedSortBitonicSequence( values, d+1, ((rank%(1<<(d+2))) < (1<<(d+1)) ) )
    # out.write(f"Iteration {d} : {values}\n")
fin = time.time()
out.write(f"Temps local pour le tri : {fin-debut} secondes\n")
out.write(f"Première valeurs locale : {values[0]}\n")
out.write(f"Dernière valeurs locale : {values[-1]}\n")
out.write(f"values : {values}\n")

out.close()
