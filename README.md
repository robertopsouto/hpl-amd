# hpl-amd
https://www.amd.com/en/developer/zen-software-studio/applications/spack/hpl-benchmark.html

## Introduction

High-Performance Linpack (HPL) is a software package that solves a (random) dense linear system in double precision (64 bits) arithmetic on distributed-memory computers. It can thus be regarded as a portable as well as freely available implementation of the High Performance Computing Linpack benchmark.

The algorithm used by HPL can be summarized by the following keywords: Two-dimensional block-cyclic data distribution - Right-looking variant of the LU factorization with row partial pivoting featuring multiple look-ahead depths - Recursive panel factorization with pivot search and column broadcast combined - Various virtual panel broadcast topologies - bandwidth reducing swap-broadcast algorithm - backward substitution with look-ahead of depth 1.

**Official Website:** https://www.netlib.org/benchmark/hpl/

For best benchmark scores on AMD ZEN architectures, we recommend using Zen HPL binaries which are optimized for EPYC platforms. For further details, refer to [AMD Zen HPL](https://www.amd.com/en/developer/zen-software-studio/applications/pre-built-applications/zen-hpl.html).

###  Empty heading

### Building HPL using Spack

**Please refer to** [**this link**](https://www.amd.com/en/developer/zen-software-studio/applications/spack/spack-getting-started.html) **for getting started with spack using AMD Zen Software Studio**

```bash
# Build HPL using AOCC and AOCL math libraries - Spack will autodetect the AMD CPU generation and use appropriate flags
$ spack install hpl %aocc +openmp ^amdblis threads=openmp ^openmpi fabrics=cma,ucx
```



Explanation of the command options:

| **Symbol**               | **Meaning**                                                  |
| ------------------------ | ------------------------------------------------------------ |
| %aocc                    | Build HPL using the AOCC compiler                            |
| +openmp                  | Build HPL with OpenMP support enabled                        |
| ^amdblis threads=openmp  | Use AMDBlis as the BLAS implementation and enable OpenMP support |
| ^openmpi fabrics=cma,ucx | Use OpenMPI as the MPI provider and use the CMA network for efficient intra-node communication, falling back to the UCX network fabric, if required. **Note:** It is advised to specifically set the appropriate fabric for the host system if possible. Refer to [Open MPI with AMD Zen Software Studio](https://www.amd.com/en/developer/zen-software-studio/applications/spack/open-mpi-zen-studio.html) for more guidance. |

## Running HPL

Recommended steps to run HPL for maximum performance on AMD systems:

1. Configure the system with **SMT Off**
2. Create the "**run_hpl.sh"** wrapper script. This script binds the MPI process to the proper AMD processor Core Complex (CCX). In an AMD EPYC**™** CPU a CCX is a group of cores which share an L3 cache and other memory hardware..
3. Create or update the HPL.dat file based on the underlying machine architecture.

This script will launch HPL with 2 MPI ranks per L3 cache, and each rank having 4 OpenMP worker threads. To change this behavior update **OMP_NUM_THREADS** and the values **x** **,y** in the **ppr:x:l3cache:pe=y** option to **mpirun.**
**Note:** Some AMD EPYC CPUs have fewer than 8 CPUs per l3cache and should use a different MPI/OpenMP layout:

- Some frequency optimized CPUs, such as EPYC™ 72F3 ("F" parts), have fewer than 8 cores per L3 cache. For such CPUs, it is recommended to use a single rank per L3 cache and set OMP_NUM_THREADS to the number of cores per L3 cache.
- For AMD 1st Gen EPYC™ Processors, which have 4 cores per L3 cache rather than 8, it is recommended to use OMP_NUM_THREADS=4 and a single rank per L3 cache**.**

**run_hpl.sh**

```bash
#! /bin/bash
# Load HPL into environment
# NOTE: If you have built multiple versions of HPL with Spack you may need to be
# more specific about which version to load. Spack will complain if your request
# is ambiguous and could refer to multiple packages.
# Please see: (https://spack.readthedocs.io/en/latest/basic_usage.html#ambiguous-specs)
spack load hpl %aocc

### Performance settings ###
# System level tunings
echo 3 > /proc/sys/vm/drop_caches   # Clear caches to maximize available RAM
echo 1 > /proc/sys/vm/compact_memory # Rearrange RAM usage to maximise the size of free blocks
echo 0 > /proc/sys/kernel/numa_balancing # Prevent kernel from migrating threads overzealously
echo 'always' > /sys/kernel/mm/transparent_hugepage/enabled # Enable hugepages for better TLB usage
echo 'always' > /sys/kernel/mm/transparent_hugepage/defrag  # Enable page defragmentation and coalescing

# Capture system specification and OpenMP settings
CORES_PER_L3CACHE=8
NUM_CORES=$(nproc)
# Use 4 threads per MPI rank  - this means 2 ranks per CPU L3cache (Zen 2+) or 1 rank per L3 (Zen 1), If using an "F" part (e.g 75F3) also ensure that OMP_NUM_THREADS is set appropriately
# (Recommended OMP_NUM_THREADS= #cores per L3 cache)
export OMP_NUM_THREADS=4
export OMP_PROC_BIND=TRUE  # bind threads to specific resources
export OMP_PLACES="cores"   # bind threads to cores

# AMDBlis (BLAS layer) optimizations
export BLIS_JC_NT=1  # (No outer loop parallelization)
export BLIS_IC_NT=$OMP_NUM_THREADS # (# of 2nd level threads – one per core in the shared L3 cache domain):
export BLIS_JR_NT=1 # (No 4th level threads)
export BLIS_IR_NT=1 # (No 5th level threads)

# MPI settings
MPI_RANKS=$(( $NUM_CORES / $OMP_NUM_THREADS ))
RANKS_PER_L3CACHE=$(( $CORES_PER_L3CACHE / $OMP_NUM_THREADS ))
MPI_OPTS=”-np $MPI_RANKS --bind-to core --map-by ppr:$RANKS_PER_L3CACHE:l3cache:pe=$OMP_NUM_THREADS ”

# Running HPL
mpirun $MPI_OPTS xhpl
```



## HPL.dat

Please change the following values as per the system configuration:

1. **Ns** - is the problem size and should be calculated based on system memory. Specifically, the problem size should be significantly larger than the total available L3 cache.
   To calculate a suitable value of **Ns** for a desired memory footprint, use the formula 
   **Ns = sqrt(M \* (1024^3)/8 )** 
   where **M** should be the desired memory usage in **Gigabytes (Gb)**.

Sample HPL.dat for dual socket AMD 5th Gen EPYC™ 9755 Processor with 256 (128x2) cores and 1.5 TB of memory.

| MPI Ranks | Ps   | Qs   |
| --------- | ---- | ---- |
| 16        | 4    | 4    |
| 24        | 4    | 6    |
| 32        | 4    | 8    |
| 48        | 6    | 8    |
| 64        | 8    | 8    |

**HPL.dat**

```bash
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out     output file name (if any)
6           device out (6=stdout,7=stderr,file)
1           # of problems sizes (N)
430080      Ns  <--- Modify this to change the memory footprint
1           # of NBs
456         # NBs
0           MAP process mapping (0=Row-,1=Column-major)
1           # of process grids (P x Q)
8           Ps <--- Set Ps and Qs to a suitable grid size
8           Qs <--- make sure that Ps * Qs == #MPI Ranks
16.0        threshold
1           # of panel fact<
1           PFACTs (0=left, 1=Crout, 2=Right)
1           # of recursive stopping criterium
4           NBMINs (>= 1)
1           # of panels in recursion
2           NDIVs
1           # of recursive panel fact.
1           RFACTs (0=left, 1=Crout, 2=Right)
1           # of broadcast
3           BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1           # of lookahead depth
0           DEPTHs (>=0)
2           SWAP (0=bin-exch,1=long,2=mix)
64          swapping threshold
0           L1 in (0=transposed,1=no-transposed) form
0           U in (0=transposed,1=no-transposed) form
1           Equilibration (0=no,1=yes)
8           memory alignment in double (> 0)
```



Once the wrapper script **(run_hpl.sh)** and a suitable **HPL.dat** have been created, run HPL by executing the wrapper script:

**Running HPL using the wrapper script**

```bash
$ chmod +x ./run_hpl.sh   # make the script executable
$ ./run_hpl.sh
```



**Note:** The above build and run steps are tested with HPL-2.3, AOCC-5.0.0, AOCL-5.0.0 and OpenMPI-5.0.5 on Red Hat Enterprise Linux release 8.9 (Ootpa) using Spack v0.23.0.dev0 (commit id : 2da812cbad ).

For [technical support](https://www.amd.com/en/developer/aocc/toolchain-technical-support.html) on the tools, benchmarks and applications that AMD offers on this page and related inquiries, reach out to us at [toolchainsupport@amd.com](mailto:toolchainsupport@amd.com). 
