from mpi4py import MPI
import numpy as np

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank

N = 360
NLoc = N//nbp + (1 if N%nbp > rank else 0)
loc_array = np.array([NLoc*rank+i for i in range(NLoc)],dtype=np.int64)
print(f"local array : {loc_array}")
glob_array = None
if rank==0: glob_array = np.empty(N,dtype=np.int64)

globCom.Gather(loc_array, glob_array)

if rank==0: print(f"global array: {glob_array}")
