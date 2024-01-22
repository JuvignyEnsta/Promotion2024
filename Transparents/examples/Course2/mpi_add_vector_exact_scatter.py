import numpy as np
from mpi4py import MPI

def assembleLocalVectors( ibeg : int, iend : int ):
    assert(iend>ibeg)
    u = np.array([-0.49*i+1. for i in range(ibeg, iend)])
    v = np.array([ 0.50*i-1. for i in range(ibeg, iend)])
    return u,v

N : int = 360
comGlobal = MPI.COMM_WORLD.Dup()
rank      = comGlobal.rank
nbp       = comGlobal.size

bufferFilename = f"output{rank:03d}.txt"
out = open(bufferFilename, 'w')

if N%nbp != 0:
    print(f"Must have a number of processes which divides the dimension {N} of the vectors")
    comGlobal.Abort(-1)

NLoc : int = N//nbp
ibeg : int = rank * NLoc
iend : int = (rank+1)*NLoc

uLoc, vLoc = assembleLocalVectors(ibeg, iend)
wLoc = uLoc + vLoc

out.write(f"{uLoc} + {vLoc} = {wLoc}\n")

out.close()
