#Author: Shebuti Rayana
#from __future__ import division
from collections import defaultdict
import math
import sys
import csv

def codeTable(filename, output, dictionary):
    with open(filename, 'r') as f:
        data = f.readlines()
    f.close()

    fq = defaultdict(int)
    rev = defaultdict(list)
    N = 0
    for d in data:
        pair = d.split()
        #print(pair)
        if len(pair) > 1:
            fq[pair[1]] += 1
            rev[pair[0]].append(pair[1])
            N = N + 1

    print(N)
    writer = csv.writer(open(dictionary, 'wb'))
    for key, value in fq.items():
        #print(key, value)
        writer.writerow([key, float(value)])

    writer = csv.writer(open(output, 'wb'))
    for key, value in rev.items():
        entropy = 0.0
        for wd in value:
            p = float(fq[wd])/N
            temp = -math.log(p, 2)
            entropy += temp
        writer.writerow([key, entropy])

if __name__ == "__main__":
    x = str(sys.argv[1])
    y = str(sys.argv[2])
    z = str(sys.argv[3])
    sys.stdout.write(str(codeTable(x,y,z)))
