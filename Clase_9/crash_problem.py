from multiprocessing import Process, Value
import ctypes

# Shared counter
counter = Value(ctypes.c_int, 0)

# Number of increments per process
num_increments = 10000

# Function to increment the counter
def increment_counter(counter):
    for _ in range(num_increments):
        counter.value += 1

def decrement_counter(counter):
    for _ in range(num_increments):
        counter.value -= 1

# Create two processes that increment the counter
process1 = Process(target=increment_counter, args=(counter,))
process2 = Process(target=decrement_counter, args=(counter,))

# Start the processes
process1.start()
process2.start()

# Wait for both processes to finish
process1.join()
process2.join()

# Print the counter
print(counter.value)
