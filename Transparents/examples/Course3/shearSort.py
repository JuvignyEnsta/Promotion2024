import numpy as np
import time
from mpi4py import MPI
import sys
from math import sqrt, log2

out = None

def oddEvenSort( values, comm : MPI.Comm):
    NLoc = values.shape[0]
    prevBuffer = np.empty((NLoc), dtype=np.int64)
    nextBuffer = np.empty((NLoc), dtype=np.int64)
    status     = MPI.Status()
    nbp = comm.size
    rank= comm.rank

    for iter in range(nbp):
        if iter%2 == 1: # Si iter est impair
            if rank%2 == 0:
                if rank > 0:
                    comm.Recv([prevBuffer,MPI.INT64_T], rank-1, status=status )
                    comm.Ssend([values,MPI.INT64_T], rank-1)
                    fusion = np.concatenate((prevBuffer, values))
                    fusion.sort(kind="mergesort")
                    values = fusion[-NLoc:] # On garde la partie supérieure
            elif rank<nbp-1: #rank est impair
                comm.Ssend([values,MPI.INT64_T], rank+1)
                comm.Recv([nextBuffer,MPI.INT64_T], rank+1, status=status)
                fusion = np.concatenate((values,nextBuffer))
                fusion.sort(kind="mergesort")
                values = fusion[:NLoc] # On garde la partie inférieure
        else: # Si iter est pair
            if rank%2 ==0:
                if rank < nbp-1:
                    comm.Recv([nextBuffer,MPI.INT64_T], rank+1, status=status)
                    comm.Ssend([values,MPI.INT64_T], rank+1)
                    fusion = np.concatenate((values, nextBuffer))
                    fusion.sort(kind="mergesort")
                    values = fusion[:NLoc] # On garde la partie inférieure
            else:
                comm.Ssend([values,MPI.INT64_T], rank-1)
                comm.Recv([prevBuffer,MPI.INT64_T], rank-1, status=status )
                fusion = np.concatenate((prevBuffer, values))
                fusion.sort(kind="mergesort")
                values = fusion[-NLoc:] # On garde la partie supérieure
    return values

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

nbRowBlocks = int(sqrt(nbp+0.1))
assert(nbRowBlocks*nbRowBlocks == nbp)

N = 360_000

if len(sys.argv) > 1:
    N = int(sys.argv[1])

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

reste= N % nbp
assert(reste == 0)
NLoc = N//nbp
out.write(f"Nombre de valeurs locales : {NLoc}`\n")


# Création de la grille de processus :
IProc = rank//nbRowBlocks
JProc = rank % nbRowBlocks if  IProc%2 == 0 else nbRowBlocks-1-rank%nbRowBlocks
rowComm = globCom.Split(IProc, rank)
colComm = globCom.Split(JProc, rank)
out.write(f"Grid coordinate : {IProc}, {JProc}\n")
nbpRow = rowComm.size
rankRow= rowComm.rank
nbpCol = colComm.size
rankCol= colComm.rank
out.write(f"Communicateur ligne   : {rankRow}/{nbpRow}\n")
out.write(f"Communicateur colonne : {rankCol}/{nbpCol}\n")

# Génération du tableau local de valeurs
values = np.random.randint(-32768, 32768, size=NLoc,dtype=np.int64)
out.write(f"Valeurs initiales : {values}\n")


debut = time.time()
nbIter = int(log2(nbp)+1)//2 + 1
values = np.sort(values)
if nbp>1:
    for iter in range(nbIter):
        out.write(f"iter : {iter}\n")
        # Row sort :
        values = oddEvenSort( values, rowComm)
        assert(len(values) == NLoc)
        # Colum sort :
        values = oddEvenSort( values, colComm)
        assert(len(values) == NLoc)
fin = time.time()
assert(len(values) == NLoc)
out.write(f"Temps local pour le tri : {fin-debut} secondes\n")
out.write(f"Première valeurs locale : {values[0]}\n")
out.write(f"Dernière valeurs locale : {values[-1]}\n")
out.write(f"values : {values}\n")

out.close()
