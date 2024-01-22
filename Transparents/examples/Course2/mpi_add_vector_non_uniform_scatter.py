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

NLoc  : int = N//nbp
reste : int = N%nbp
if reste>rank: NLoc += 1
ibeg : int = rank * NLoc + reste if rank>=reste else rank * NLoc
iend : int = ibeg + NLoc

uLoc, vLoc = assembleLocalVectors(ibeg, iend)
wLoc = uLoc + vLoc

out.write(f"{uLoc} + {vLoc} = {wLoc}\n")

out.close()
