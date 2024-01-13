import numpy as np
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

# Envoie par sérialisation : le plus simple mais le moins performant !
# En effet, ce send sérialise et compresse les données afin de pouvoir
# envoyer toute donnée "sérialisable" sous forme compressée à l'autre processus
out.write("Envoie/reception donnees heterogenes\n")
liste_recue = None
if rank == 0:
    une_liste = [ "Chien", 3.14, "Chat", 404, 4+3.j]
    globCom.send(une_liste, dest=1, tag=101)
    liste_recue = globCom.recv(source=1, tag=102)
elif rank==1:
    une_liste = [ "Alice", 131, ("Bob", 5.2), [2,3,5,7,11]]
    liste_recue = globCom.recv(source=0, tag=101)
    globCom.send(une_liste, dest=0, tag=102)

out.write(f"Liste recue : {liste_recue}\n")

# Envoie directement les donnees d'un tableau numpy sans passer par la serialisation
# C'est plus efficace lorsqu'on passe que des données de type homogène
out.write("Envoie/reception donnees homogenes\n")
data = None
if rank == 0:
    un_buffer = np.array([1.,3.,5.,7.],dtype=np.double)
    globCom.Send([un_buffer, MPI.DOUBLE], dest=1, tag=101)
    data = np.empty(4, dtype=np.double)
    globCom.Recv([data, MPI.DOUBLE], source=1, tag=102)
elif rank == 1:
    un_buffer = np.array([2.,4.,6.,8.],dtype=np.double)
    data = np.empty(4, dtype=np.double)
    globCom.Recv([data, MPI.DOUBLE], source=0, tag=101)
    globCom.Send([un_buffer, MPI.DOUBLE], dest=0, tag=102)

out.write(f"data recue : {data}\n")
out.close()
