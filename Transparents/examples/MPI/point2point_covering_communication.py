import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

if rank==0:
    tab = np.array([2.,3.,5.,7.,11.,13.,17.], dtype=np.double)
    # Non blocking send to compute sum of inverse at the same time than data is sended
    req = globCom.Isend([tab,MPI.DOUBLE], dest=1, tag=101)
    accum = 0.
    for v in tab:
        accum += 1./v
    out.write(f"Inverse sum : {accum}\n")
    req.wait()
elif rank==1:
    tab = np.empty(7, dtype=np.double)
    # Non blocking receive
    req = globCom.Irecv([tab,MPI.DOUBLE], source=0, tag=101)
    while (req.Test() == False):
        out.write("Computing other data while waiting data from 0\n")
    accum = 0.
    for v in tab:
        accum += 1./v
    out.write(f"Inverse sum : {accum}\n")

out.close()
