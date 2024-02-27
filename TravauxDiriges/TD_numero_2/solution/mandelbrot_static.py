# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from mpi4py import MPI

global_com = MPI.COMM_WORLD.Dup()
rank       = global_com.rank
nbp        = global_com.size

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius : float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c:complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c,smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float :
        z    : complex
        iter : int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625 :
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}    
        if (c.real > -0.75) and (c.real < 0.5) :
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2,1.E-14)):
                return self.max_iterations
        # Sinon on itère 
        z=0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=500,escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height
# Calcul de l'ensemble de mandelbrot :
# Calcul du nombre de lignes à calculer par processeurs :
H_locals = np.array([height//nbp + (1 if height%nbp > i_rank else 0) for i_rank in range(nbp)], dtype=np.int32)
convergence = np.empty((H_locals[rank], width),dtype=np.double)
# Calcul du début des lignes à calcul par noeud de calcul :
first_rows = np.zeros(nbp, dtype=np.int32)
for i_rank in range(1,nbp):
    first_rows[i_rank] = first_rows[i_rank-1] + H_locals[i_rank-1]

deb = time()
for y in range(H_locals[rank]):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * (y+first_rows[rank]))
        convergence[y,x] = mandelbrot_set.convergence(c,smooth=True)

convergence_glob = np.empty((height,width), dtype=np.double)
fin = time()
out.write(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb}\n")
global_com.Gatherv(convergence, convergence_glob, 0)

# Constitution de l'image résultante :
if (rank==0):
    deb=time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence_glob)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()

out.close()
