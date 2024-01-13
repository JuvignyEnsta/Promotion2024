from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

out.write(f"Je suis le processus {rank} sur {nbp} processus\n")
out.write(f"Je m'execute sur l'ordinateur {name}\n")

out.close()
