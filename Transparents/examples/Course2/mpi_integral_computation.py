from mpi4py import MPI
from math import sin, exp
from numpy import polynomial
import time
order=64

def f(x : float) -> float:
    return abs(sin(x*x))*exp(-x*x)

a              : float = -100.
b              : float = +100.
nbSubIntervals : int   = 10_000
h              : float = (b-a)/nbSubIntervals

comGlobal = MPI.COMM_WORLD.Dup()
nbp       = comGlobal.size
rank      = comGlobal.rank

bufferFileName = f"output{rank:03d}.txt"
out = open(bufferFileName, 'w')

# Récupération du schéma de quadrature de Gauss-Legendre d'ordre order
#  quadrature contient deux tableaux : 
#     quadrature[0] contient les points d'intégration (dans [-1;1])
#     quadrature[1] contient les poids d'intégration
quadrature = polynomial.legendre.leggauss(order)

debut = time.time()
sumLoc   : float = 0.
nbSubLoc : int   = nbSubIntervals//nbp
reste    : int   = nbSubIntervals%nbp
if reste > rank :
    nbSubLoc += 1
# Calcul du premier intervalle concerné par le processus :
begSub : int = rank * nbSubLoc
if reste < rank :
    begSub += reste
for s in range(begSub, begSub+nbSubLoc):
    ai : float = a + h*s
    bi : float = ai + h
    mi : float = 0.5*(ai+bi)
    si : float = 0.
    # Gauss quadrature :
    for iGauss in range(len(quadrature[0])):
        gi : float = mi + 0.5*h*quadrature[0][iGauss]
        si += quadrature[1][iGauss] * f(gi)
    si = 0.5*h*si
    sumLoc += si
sum : float = comGlobal.reduce(sumLoc, MPI.SUM, 0)
fin = time.time()
if rank == 0:
    out.write(f"Integral_[-100;+100] sin(x*x) exp(-x*x) dx = {sum}\n")
out.write(f"Temps pour calculer l'intégrale : {fin-debut} secondes\n")
