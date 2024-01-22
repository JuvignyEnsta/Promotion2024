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

# Récupération du schéma de quadrature de Gauss-Legendre d'ordre order
#  quadrature contient deux tableaux : 
#     quadrature[0] contient les points d'intégration (dans [-1;1])
#     quadrature[1] contient les poids d'intégration
quadrature = polynomial.legendre.leggauss(order)

debut = time.time()
sum : float = 0.
for s in range(nbSubIntervals):
    ai : float = a + h*s
    bi : float = ai + h
    mi : float = 0.5*(ai+bi)
    si : float = 0.
    # Gauss Quadrature
    for iGauss in range(len(quadrature[0])):
        gi : float = mi + 0.5*h*quadrature[0][iGauss]
        si += quadrature[1][iGauss] * f(gi)
    si = 0.5*h*si
    sum += si
fin = time.time()

print(f"Integral_[-100;+100] sin(x*x) exp(-x*x) dx = {sum}")
print(f"Temps pour calculer l'intégrale : {fin-debut} secondes")
