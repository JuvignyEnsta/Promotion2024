import numpy as np

def assembleVectors( dim : int ):
    assert(dim>0)
    u = np.array([-0.49*i+1. for i in range(dim)])
    v = np.array([ 0.50*i-1. for i in range(dim)])
    return u,v

N : int = 360
u,v = assembleVectors(N)
w = u + v

print(f"{u} + {v} = {w}")
