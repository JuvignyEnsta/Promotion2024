from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

print(f"Je suis le processus {rank} sur {nbp} processus")
print(f"Je m'execute sur l'ordinateur {name}")

