from mpi4py import MPI

# Initialize MPI communication
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Initialize token variable
jeton = None

# Process 0 sends the token to the next process and receives it back
if rank == 0:
    # Initialize the token
    jeton = 1
    
    # Send the token to the next process
    dest_rank = (rank + 1) % size
    comm.send(jeton, dest=dest_rank)
    
    # Receive the token from the last process
    jeton = comm.recv(source=size - 1)
    
    # Print the received token
    print(f"Process {rank} receives token {jeton} from process {size - 1}")

# Other processes receive the token from the previous process, increment it, and pass it to the next process
else:
    # Receive the token from the previous process
    source_rank = (rank - 1) % size
    jeton = comm.recv(source=source_rank)
    
    # Print the received token
    print(f"Process {rank} receives token {jeton} from process {(rank - 1) % size}")
    
    # Increment the token
    jeton += 1
    
    # Send the token to the next process
    dest_rank = (rank + 1) % size
    comm.send(jeton, dest=dest_rank)

# Finalize MPI communication
MPI.Finalize()
