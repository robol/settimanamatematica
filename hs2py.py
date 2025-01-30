#!/usr/bin/env python3

import sys, re

c = []
p = []

with open(sys.argv[1], "r") as h:
    for line in h:
        ll = re.sub(r",?Harmonic \d+\w*", "", line)
        ll = ll.strip().replace("(", "").replace(")", "").split()
        c.append(float(ll[1]))
        p.append(float(ll[0]))

print("p = ", end = "")
print(p)
print("c = ", end = "")
print(c)
