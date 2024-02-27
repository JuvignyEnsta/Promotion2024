# Produit matrice-vecteur v = A.u
import numpy as np
from mpi4py import MPI

global_com = MPI.COMM_WORLD.Dup()
rank       = global_com.rank
nbp        = global_com.size

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

# Dimension du problème (peut-être changé)
dim = 120
# Calcul du nombre de lignes local :
nb_row_loc = dim//nbp
# Calcul de la première ligne prise en compte par la matrice locale :
first_row  = nb_row_loc * rank
# Initialisation de la matrice
A_local = np.array([ [(i+first_row+j)%dim+1. for j in range(dim)] for i in range(nb_row_loc) ])
out.write(f"A_local = {A_local}\n")

# Initialisation du vecteur u
u = np.array([i+1. for i in range(dim)])
out.write(f"u = {u}\n")

# Produit matrice-vecteur
v_local = A_local.dot(u)
out.write(f"v_local = {v_local}\n")

v = np.empty(dim, v_local.dtype)
global_com.Allgather(v_local, v)

out.write(f"v = {v}\n")
out.close()
