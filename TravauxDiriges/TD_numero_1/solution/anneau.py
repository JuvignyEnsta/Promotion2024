from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

if rank==0:
    jeton = 1
    globCom.send(jeton, dest=1)
    jeton = globCom.recv(source=nbp-1)
    print(f"jeton = {jeton}")
else:
    jeton = globCom.recv(source=rank-1)
    jeton += rank+1
    globCom.send(jeton, dest=(rank+1)%nbp)
