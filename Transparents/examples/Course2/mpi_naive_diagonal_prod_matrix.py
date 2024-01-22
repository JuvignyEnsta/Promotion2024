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

# Partage des tâches :
# --------------------
reste = nbBlocks % nbp
NBlockLoc : int = nbBlocks//nbp + (1 if reste > rank else 0)
firstBlock: int = NBlockLoc * rank + (reste if (rank>=reste) else 0)
out.write(f"Nombre de blocs locaux : {NBlockLoc}\n")
out.write(f"Indice premier bloc local : {firstBlock}\n")
# Initialisation des blocs diagonaux locaux de A et B
# ---------------------------------------------------
# A_ii est sous la forme U_{a}.V_{a}^{T} (produit tensoriel de deux vecteurs)
# B_ii est sous la forme U_{b}.V_{b}^{T} (produit tensoriel de deux vecteurs)
#
debut = time.time()
A = []
B = []
begRow : int = 0
firstRowLoc : int = -1
for iBlock in range(nbBlocks):
    locDim : int = 10*(iBlock+1)
    if iBlock == firstBlock : firstRowLoc = begRow
    if (iBlock >= firstBlock) and (iBlock < firstBlock + NBlockLoc):
        A.append(generateDiagonalBlock(locDim, freq1, begRow))
        B.append(generateDiagonalBlock(locDim, freq2, begRow))
    begRow += locDim
fin = time.time()
out.write(f"Temps d'assemblage des blocs : {fin-debut} secondes\n")
out.write(f"Nombre blocs stockés local : {len(A)} \n")
# Calcul des blocs diagonaux de C = A.B
debut = time.time()
C = []
for iBlock in range(NBlockLoc):
    C.append(A[iBlock].dot(B[iBlock]))
fin   = time.time()
out.write(f"Temps produit des blocs diagonaux : {fin-debut} secondes\n")

# Vérification des blocs diagonaux calculés pour C :
# -------------------------------------------------
# Un bloc de C se calcul en fait comme : C_{ii} = (Va^{T}.Ub) Ua.Vb^{T}
debut = time.time()
for iBlock in range(NBlockLoc):
    if (not verifyBlockOfC(firstRowLoc, freq1, freq2, C[iBlock])) :
        print(f"Erreur dans le calcul du bloc numero {iBlock}")
    firstRowLoc += C[iBlock].shape[0]
fin = time.time()
out.write(f"Temps pris pour la verification des blocs diagonaux de C : {fin-debut} secondes\n")
