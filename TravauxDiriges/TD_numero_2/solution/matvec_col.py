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
# Calcul du nombre de colonnes local:
nb_col_loc = dim//nbp
# Calcul de la première colonne prise en compte pour la matrice locale :
first_col   = nb_col_loc * rank
# Initialisation de la matrice
A_local = np.array([ [(i+j+first_col)%dim+1. for j in range(nb_col_loc)] for i in range(dim) ])
out.write(f"A_local = {A_local}\n")

# Initialisation du vecteur u
u_local = np.array([i+first_col+1. for i in range(nb_col_loc)])
out.write(f"u_local = {u_local}\n")

# Produit matrice-vecteur
v_partial = A_local.dot(u_local)
out.write(f"v_partial = {v_partial}\n")

v = np.empty(dim, dtype=v_partial.dtype)
global_com.Allreduce(v_partial, v )

out.write(f"v = {v}\n")

out.close()
