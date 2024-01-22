# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import pi
from time import time
import matplotlib.cm
from mpi4py import MPI

twoPi = 2.*pi

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius : float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c:complex, clamp=True) -> float:
        value = self.count_iterations(c)[0]/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex) :
        iter : int
        z = []
        z.append(c)
        for iter in range(self.max_iterations):
            z.append(z[-1]*z[-1] + c)
            if abs(z[-1]) > self.escape_radius:
                return iter, np.array(z[:-1],dtype=np.complex128)
        return self.max_iterations,np.array([],dtype=np.complex128)

# Definition d'une tâche prenant un sous paquet de samples à traiter :
def bhuddabort_task(nbSamples : int, maxIter : int, width : int, height : int ):
    radius = 2*np.random.rand(nbSamples)
    angle  = twoPi*np.random.rand(nbSamples)
    scaleX = 0.25*width
    scaleY = 0.25*height
    image = np.zeros((width, height),dtype=np.int64)
    cArr = radius*(np.cos(angle)+np.sin(angle)*1j)
    mandelbrot_set = MandelbrotSet(max_iterations=maxIter)
    for c in cArr:
        niter, orbit = mandelbrot_set.count_iterations(c)
        if niter < maxIter:
            x = np.asarray(scaleX*(orbit.real+2.),dtype=np.int32)
            y = np.asarray(scaleY*(orbit.imag+2.),dtype=np.int32)
            mask = np.logical_and(x<width, y<height)
            xfiltre = x[np.where(mask)]
            yfiltre = y[np.where(mask)]
            image[xfiltre,yfiltre] += 1
    return image

# Bhuddabrot to test the chronometer
def bhuddabrot ( nbSamples : int, maxIter : int, width : int, height : int, comm : MPI.Comm ):
    packSize = 64
    nbp      = comm.size
    rank     = comm.rank

    nbPacks = (nbSamples+packSize-1)//packSize
    image     = np.zeros((width, height),dtype=np.int64)
    image_loc = np.zeros((width, height),dtype=np.int64)
    # Algorithme maître-escalve :
    if rank==0: # Algorithme maître distribuant les tâches

        iPack : int = 0
        for iProc in range(1,nbp):
            comm.send(iPack, iProc)
            iPack += 1
        stat : MPI.Status = MPI.Status()
        while iPack < nbPacks:
            done = comm.recv(status=stat)# On reçoit du premier process à envoyer un message
            slaveRk = stat.source
            comm.send(iPack, dest=slaveRk)
            iPack += 1
        iPack = -1 # iPack vaut maintenant -1 pour signaler aux autres procs qu'il n'y a plus de tâches à exécuter
        for iProc in range(1,nbp):
            status = MPI.Status()
            done = comm.recv(status=status)# On reçoit du premier process à envoyer un message
            slaveRk : int = status.source
            comm.send(iPack, dest=slaveRk)
        comm.Reduce([image_loc,MPI.INT64_T], [image,MPI.INT64_T], op=MPI.SUM, root=0)
    else:
        status : MPI.Status = MPI.Status()
        iPack : int
        res   : int = 1

        iPack = comm.recv(source=0) # On reçoit un n° de tâche à effectuer
        while iPack != -1:          # Tant qu'il y a une tâche à faire
            image_loc = bhuddabort_task(packSize, maxIter, width, height )
            req : MPI.Request = comm.isend(res,0)
            image += image_loc
            iPack = comm.recv(source=0) # On reçoit un n° de tâche à effectuer
            req.wait()
        comm.Reduce([image,MPI.INT64_T], None, op=MPI.SUM, root=0)
    return image

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

filename = f"Output{rank:03d}.txt"
out      = open(filename, mode='w')

# On peut changer les paramètres des deux prochaines lignes
width, height = 1024, 1024

# Calcul de chaque composante de Bhuddabrot
s1 = 1500_000 #150_000
s2 =  500_000 # 50_000
s3 =    30000 # 3_000
deb = time()
out.write("red\n")
redOrbit   = bhuddabrot( s1,  2_000, width, height, globCom)
out.write("green\n")
greenOrbit = bhuddabrot(  s2, 10_000, width, height, globCom)
out.write("blue\n")
blueOrbit  = bhuddabrot(   s3, 10_000, width, height, globCom)
fin = time()
out.write(f"Temps du calcul de l'ensemble de Bhuddabrot : {fin-deb} secondes\n")

if rank==0:
    # Constitution de l'image résultante :
    deb=time()
    b1 = np.sum(redOrbit)
    b2 = np.sum(greenOrbit)
    b3 = np.sum(blueOrbit)
    stride : int = width*height
    scal1 : float = 16.*stride/b1
    scal2 : float = 16.*stride/b2
    scal3 : float = 16.*stride/b3
    red   = np.array(np.clip((scal1*redOrbit).astype(np.uint8),0,255))
    green = np.array(np.clip((scal2*greenOrbit).astype(np.uint8),0,255))
    blue  = np.array(np.clip((scal3*blueOrbit).astype(np.uint8),0,255))
    pixels = np.stack((red,green,blue),axis=-1)
    image = Image.fromarray(pixels, 'RGB')
    fin = time()
    out.write(f"Temps de constitution de l'image : {fin-deb} secondes\n")
    image.save("bhudda.jpg")
