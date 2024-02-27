import numpy as np
import time
from mpi4py import MPI
import sys
from math import sqrt, log2
import itertools

out  = None
DEBUG= 0

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

N = 256_000

if len(sys.argv) > 1:
    N = int(sys.argv[1])

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

reste= N % nbp
NLoc = N//nbp + (1 if reste < rank else 0)
out.write(f"Nombre de valeurs locales : {NLoc}`\n")

# Génération du tableau local de valeurs
values = np.random.randint(-32768, 32768, size=NLoc,dtype=np.int64)
out.write(f"Valeurs initiales : {values}\n")

debut = time.time()
# Tri local
values.sort()
# Choix des pivots pour obtenir des buckets optimisant la distribution du tableau local
step_pivots = NLoc//nbp
pivots = np.array(values[step_pivots : : step_pivots])
pivots = pivots[:nbp-1] # Dans le cas où NLoc n'est pas divvsible par nbp, on peut avoir le dernier élément de values en plus dans notre tableau
                        # On le vire donc du tableau
if DEBUG: out.write(f"Pivots locaux selectionnes : {pivots}\n")

# Diffusion des pivots locaux sur tous les autres processeurs :
all_pivots = np.empty(nbp*(nbp-1),dtype=np.int64)
globCom.Allgather(pivots, all_pivots)
all_pivots.sort(kind="mergesort")

# Puis on choisit le median de chaque pivot :
glob_pivots = all_pivots[nbp//2::nbp]

# On range les valeurs dans des seaux locaux :
local_buckets = []
## Traitement spécial pour le proc 0 :
local_buckets.append( np.array(values[values <= glob_pivots[0]]))
## Pour les buckets 1 à nbp-1 :
for p in range(1,nbp-1):
    local_buckets.append( np.array(values[np.logical_and(values <= glob_pivots[p],values > glob_pivots[p-1])]) )
## Traitement spécial pour le dernier proc :
local_buckets.append( np.array(values[values > glob_pivots[-1]]) )
if DEBUG: out.write(f"local buckets : {local_buckets}\n")

# On collecte les seaux des divers processeurs, processeur par processeur
my_values = None
for p in range(nbp):
    if p == rank :
        my_values = globCom.gather(local_buckets[p], root=p)
    else:
        globCom.gather(local_buckets[p], root=p)

sorted_loc_values = np.array(list(itertools.chain.from_iterable(my_values)),dtype=np.int64)
sorted_loc_values.sort()
fin = time.time()

out.write(f"Temps local pour le tri : {fin-debut} secondes\n")
if sorted_loc_values.shape[0] > 0:
    out.write(f"Première valeurs locale : {sorted_loc_values[0]}\n")
    out.write(f"Dernière valeurs locale : {sorted_loc_values[-1]}\n")
    out.write(f"values : {sorted_loc_values}\n")
    out.write(f"Number of local values after sorted : {sorted_loc_values.shape[0]}\n")

out.close()
