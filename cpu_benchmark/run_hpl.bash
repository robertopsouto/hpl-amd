#!/bin/bash

### Performance settings ###
# System level tunings
#echo 3 > /proc/sys/vm/drop_caches   # Clear caches to maximize available RAM
#echo 1 > /proc/sys/vm/compact_memory # Rearrange RAM usage to maximise the size of free blocks
#echo 0 > /proc/sys/kernel/numa_balancing # Prevent kernel from migrating threads overzealously
#echo 'always' > /sys/kernel/mm/transparent_hugepage/enabled # Enable hugepages for better TLB usage
#echo 'always' > /sys/kernel/mm/transparent_hugepage/defrag  # Enable page defragmentation and coalescing

# Capture system specification and OpenMP settings
CORES_PER_L3CACHE=8
NUM_CORES=192
# Use 4 threads per MPI rank  - this means 2 ranks per CPU L3cache (Zen 2+) or 1 rank per L3 (Zen 1), If using an "F" part (e.g 75F3) also ensure that OMP_NUM_THREADS is set appropriately
# (Recommended OMP_NUM_THREADS= #cores per L3 cache)
export OMP_NUM_THREADS=$((CORES_PER_L3CACHE / 2))
export OMP_PROC_BIND=TRUE  # bind threads to specific resources
export OMP_PLACES="cores"   # bind threads to cores

# AMDBlis (BLAS layer) optimizations
export BLIS_JC_NT=1  # (No outer loop parallelization)
export BLIS_IC_NT=$OMP_NUM_THREADS # (# of 2nd level threads – one per core in the shared L3 cache domain):
export BLIS_JR_NT=1 # (No 4th level threads)
export BLIS_IR_NT=1 # (No 5th level threads)

# MPI settings
#MPI_RANKS=$(( $NUM_CORES / $OMP_NUM_THREADS ))
MPI_RANKS=24
RANKS_PER_L3CACHE=$(( $CORES_PER_L3CACHE / $OMP_NUM_THREADS ))
MPI_OPTS="-np $MPI_RANKS --bind-to core --map-by ppr:$RANKS_PER_L3CACHE:l3cache:pe=$OMP_NUM_THREADS"

echo "Running HPL"
echo "mpirun $MPI_OPTS xhpl"
# Running HPL
mpirun $MPI_OPTS xhpl
