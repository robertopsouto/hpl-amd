#!/usr/bin/python3
import sys
import os
import os.path
import subprocess
import shutil
import math
import re
import argparse

import os
import sys
import math


def gcd(a,b) :
  while a%b != 0 :
    a, b = b, a%b
  return b

def lcm(a,b):
  return a*b/gcd(a,b)

def find_divisors(v):
  i=1
  divisors=[]
  sqrt_v=math.sqrt(v)
  while i <= sqrt_v:
    if v%i==0:
      divisors.append(i)
    i+=1
  return divisors



#######################
# program main
#
if __name__ == "__main__":


  parser = argparse.ArgumentParser(description="BULL HPL Utility")
  parser.add_argument("--compute", help="compute: p,q,N")
  parser.add_argument("--nb", type=int,default=384)
  parser.add_argument("--mem-per-task", type=int)
  parser.add_argument("--ppn", type=float,default=1.0)
  parser.add_argument("--tasks", type=int,help="tasks")
  args = parser.parse_args()
  if (not args.tasks) or (not args.nb) or not (args.compute):
    print("please check parameters")
    sys.exit(1)

  divs=find_divisors(args.tasks)
  last=-1
  test=0
  while test == 0 :
    if args.tasks ==1 :
          selected_p=1
          selected_q=1
          test=1
          continue
    if args.tasks == 2 :
          selected_p=1
          selected_q=2
          test=1
          continue

    selected_p=divs[last]
    selected_q=args.tasks/selected_p
    #print(selected_p,selected_q)
    if selected_p%4 == 0 or selected_q%4 == 0 :
        test=1
    else:
        last=last-1

  if selected_p%4 != 0 :
    t=selected_p
    selected_p=selected_q
    selected_q=t

  if args.tasks == 4 :
    selected_p=2
    selected_q=2


  if args.compute in['P','Q']:
    if args.compute=='P':
      print(int(selected_p))
    else:
      print(int(selected_q))
  if args.compute=='N':
    #tot_mem=args.mem_per_task*4
    tot_mem=args.mem_per_task*args.tasks
    #N=int(math.sqrt(((tot_mem*args.mem_ratio))))
    #N=int(math.ceil(math.sqrt(args.mem_per_task* 2**24 / 8 * selected_p*selected_q)))
    #N=int(math.ceil(math.sqrt(args.mem_per_task* (1024**3)/8 )))
    N=int(math.ceil(math.sqrt(tot_mem* (1024**3)/8 )))
    rem = N % (args.nb)
    if rem == 0:
        print(N)
    print(N+(args.nb)-rem)


    #N=int(math.sqrt(((tot_mem*1024*1024*1024)/8.0)*args.mem_ratio))
    #granu=args.nb*lcm(selected_p,selected_q)
    #N=int(math.floor(N/granu)*granu)
    #print(N)



