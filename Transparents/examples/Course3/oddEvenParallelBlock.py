import numpy as np
import time
from mpi4py import MPI
import sys


globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

N = 360_000

if len(sys.argv) > 1:
    N = int(sys.argv[1])

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

reste= N % nbp
NLoc = N//nbp + ( 1 if reste > rank else 0)
out.write(f"Nombre de valeurs locales : {NLoc}`\n")


values = np.random.randint(-32768, 32768, size=NLoc,dtype=np.int64)
out.write(f"Valeurs initiales : {values}\n")

debut = time.time()
values = np.sort(values)
prevNbLoc = N//nbp + (1 if reste > rank-1 else 0)
nextNbLoc = N//nbp + (1 if reste > rank+1 else 0)
prevBuffer = np.empty((prevNbLoc), dtype=np.int64)
nextBuffer = np.empty((nextNbLoc), dtype=np.int64)
status     = MPI.Status()
for iter in range(nbp):
    out.write(f"iter {iter}\n")
    if iter%2 == 1: # Si iter est impair
        if rank%2 == 0:
            if rank > 0:
                globCom.Recv([prevBuffer,MPI.INT64_T], rank-1, status=status )
                globCom.Ssend([values,MPI.INT64_T], rank-1)
                fusion = np.concatenate((prevBuffer, values))
                fusion.sort(kind="mergesort")
                values = fusion[-NLoc:] # On garde la partie supérieure
        elif rank<nbp-1: #rank est impair
            globCom.Ssend([values,MPI.INT64_T], rank+1)
            globCom.Recv([nextBuffer,MPI.INT64_T], rank+1, status=status)
            fusion = np.concatenate((values,nextBuffer))
            fusion.sort(kind="mergesort")
            values = fusion[:NLoc] # On garde la partie inférieure
    else: # Si iter est pair
        if rank%2 ==0:
            if rank < nbp-1:
                globCom.Recv([nextBuffer,MPI.INT64_T], rank+1, status=status)
                globCom.Ssend([values,MPI.INT64_T], rank+1)
                fusion = np.concatenate((values, nextBuffer))
                fusion.sort(kind="mergesort")
                values = fusion[:NLoc] # On garde la partie inférieure
        else:
            globCom.Ssend([values,MPI.INT64_T], rank-1)
            globCom.Recv([prevBuffer,MPI.INT64_T], rank-1, status=status )
            fusion = np.concatenate((prevBuffer, values))
            fusion.sort(kind="mergesort")
            values = fusion[-NLoc:] # On garde la partie supérieure
fin = time.time()
assert(len(values) == NLoc)
out.write(f"Temps local pour le tri : {fin-debut} secondes\n")
out.write(f"Première valeurs locale : {values[0]}\n")
out.write(f"Dernière valeurs locale : {values[-1]}\n")
out.write(f"values : {values}\n")

out.close()
