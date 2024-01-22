from math import pi, sin, cos
import numpy as np
import time
from mpi4py import MPI

twoPi : float = 2*pi

def generateDiagonalBlock(  t_dim : int, t_freq : float, t_firstInd : int ):
    ibeg : int = t_firstInd
    iend : int = ibeg + t_dim
    Ua = np.sin([twoPi * t_freq * iGlob for iGlob in range(ibeg,iend)])
    Va = np.cos([twoPi * t_freq * iGlob for iGlob in range(ibeg,iend)])
    # Génère le block diagonal :
    B = np.outer(Ua, Va)
    return B

def verifyBlockOfC(indFirstRow : int, freqA : float, freqB : float,
                   Cii):
    dim : int = Cii.shape[0]
    ibeg = indFirstRow
    iend = indFirstRow + dim
    # Calcul de s = V_a^{T}.U_b
    icos = np.cos([twoPi * freqA * iGlob for iGlob in range(ibeg, iend)])
    jsin = np.sin([twoPi * freqB * iGlob for iGlob in range(ibeg, iend)])
    prodScal : float = icos.dot(jsin)

    jcos = prodScal * np.cos([twoPi * freqB * iGlob for iGlob in range(ibeg, iend)])
    isin = np.sin([twoPi * freqA * iGlob for iGlob in range(ibeg, iend)])

    V = np.outer(isin,jcos)
    error = (Cii-V > 1.E-10)

    if np.any(error):
        print(f"Erreur dans le produit matrice-matrice : {Cii}  et matrice attendue : {V}")
        return False

    return True

def distribBlocks( t_dimensions, nbp : int, rank : int ):
    weights = np.zeros(nbp, dtype=np.double)
    # On fait un tri du tableau d'index de sorte de trier indirectement le tableau des dimensions
    # de façon décroissante
    sort_index = np.flip(np.argsort(t_dimensions))

    indexBlock = []

    # Initialisation des poids en distribuant les plus grandes dimensions sur les processus :
    weights = t_dimensions[sort_index[0:nbp]]**3
    print(weights)
    indexBlock.append(sort_index[rank])
    for p in range(nbp, len(t_dimensions)):
        dim = t_dimensions[sort_index[p]]
        # Recherche du poids le plus petit :
        iterMin = np.argmin(weights)
        weights[iterMin] += dim**3
        if iterMin == rank:
            indexBlock.append(sort_index[p])

    return indexBlock

nbBlocks : int   = 180
freq1    : float = 0.125
freq2    : float = 0.0134

# Initialisation de MPI
# ---------------------
comGlobal = MPI.COMM_WORLD.Dup()
rank      = comGlobal.rank
nbp       = comGlobal.size

bufferFilename = f"output{rank:03d}.txt"
out = open(bufferFilename, 'w')

# Calcul des dimensions et début de blocs et partage des tâches :
# ---------------------------------------------------------------
dimensions = np.array([10*(iBlock+1) for iBlock in range(nbBlocks)])
begRows    = np.zeros(nbBlocks, dtype=np.int32)
begRows[0] = 0
for i in range(1,nbBlocks):
    begRows[i] = begRows[i-1] + dimensions[i]

# Distributions des blocs pour optimiser l'équilibrage :
indexLocalBlocks = distribBlocks( dimensions, nbp, rank )
out.write(f"Distribution : {indexLocalBlocks}\n")

out.write(f"Nombre de blocs locaux : {len(indexLocalBlocks)}\n")
# Initialisation des blocs diagonaux locaux de A et B
# ---------------------------------------------------
# A_ii est sous la forme U_{a}.V_{a}^{T} (produit tensoriel de deux vecteurs)
# B_ii est sous la forme U_{b}.V_{b}^{T} (produit tensoriel de deux vecteurs)
#
debut = time.time()
nbBlocksLoc = len(indexLocalBlocks)
A = []
B = []
for index in indexLocalBlocks:
    A.append(generateDiagonalBlock(dimensions[index], freq1, begRows[index]))
    B.append(generateDiagonalBlock(dimensions[index], freq2, begRows[index]))
fin = time.time()
out.write(f"Temps d'assemblage des blocs : {fin-debut} secondes\n")
out.write(f"Nombre blocs stockés local : {len(A)} \n")
# Calcul des blocs diagonaux de C = A.B
debut = time.time()
C = []
for iBlock in range(nbBlocksLoc):
    C.append(A[iBlock].dot(B[iBlock]))
fin   = time.time()
out.write(f"Temps produit des blocs diagonaux : {fin-debut} secondes\n")

# Vérification des blocs diagonaux calculés pour C :
# -------------------------------------------------
# Un bloc de C se calcul en fait comme : C_{ii} = (Va^{T}.Ub) Ua.Vb^{T}
debut = time.time()
for iBlock in range(nbBlocksLoc):
    if (not verifyBlockOfC(begRows[indexLocalBlocks[iBlock]], freq1, freq2, C[iBlock])) :
        print(f"Erreur dans le calcul du bloc numero {iBlock}")
fin = time.time()
out.write(f"Temps pris pour la verification des blocs diagonaux de C : {fin-debut} secondes\n")
