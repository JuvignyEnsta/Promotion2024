# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import pi
from time import time
import matplotlib.cm

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

# Bhuddabrot to test the chronometer
def bhuddabrot ( nbSamples : int, maxIter : int, width : int, height : int ):
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

# On peut changer les paramètres des deux prochaines lignes
width, height = 1024, 1024

# Calcul de chaque composante de Bhuddabrot
s1 = 1500_000 #150_000
s2 =  500_000 # 50_000
s3 =    30000 # 3_000
deb = time()
print("red")
redOrbit   = bhuddabrot( s1,  2_000, width, height)
print("green")
greenOrbit = bhuddabrot(  s2, 10_000, width, height)
print("blue")
blueOrbit  = bhuddabrot(   s3, 10_000, width, height)
fin = time()
print(f"Temps du calcul de l'ensemble de Bhuddabrot : {fin-deb}")


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
print(f"Temps de constitution de l'image : {fin-deb}")
image.save("bhudda.jpg")
image.show()
