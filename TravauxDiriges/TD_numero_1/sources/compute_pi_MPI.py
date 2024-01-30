from mpi4py import MPI
import time
import numpy as np

def compute_pi(samples):
    # Generate random points within the unit square
    x = 2 * np.random.random(samples) - 1
    y = 2 * np.random.random(samples) - 1
    
    # Check if the points fall within the unit circle
    filtre = x**2 + y**2 < 1
    
    # Count the number of points inside the circle
    return np.sum(filtre)

def main():
    # Initialize MPI communication
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Number of samples for Monte Carlo simulation
    nb_samples = 40_000_000
    
    # Distribute samples evenly among processes
    samples_per_task = nb_samples // size
    
    # Start timing
    beg = time.time()

    # Compute partial sum of samples for each process
    count = compute_pi(samples_per_task)
    
    # Reduce partial sums to get total count of samples inside the circle
    total_count = comm.reduce(count, op=MPI.SUM, root=0)

    # Process 0 computes the final approximation of Pi
    if rank == 0:
        # Calculate Pi using the Monte Carlo method
        approx_pi = 4 * total_count / nb_samples
        
        # End timing
        end = time.time()
        
        # Print results
        print(f"Time taken to compute Pi: {end - beg} seconds")
        print(f"Approximate value of Pi is: {approx_pi}")

if __name__ == '__main__':
    main()
