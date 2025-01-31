#!/usr/bin/env python3

import sys, re, math

c = []
s = []

with open(sys.argv[1], "r") as h:
    j = 1
    for line in h:
        ll = re.sub(r",?Harmonic \d+\w*", "", line)
        ll = ll.strip().replace("(", "").replace(")", "").split()

        # Amplitude and phase
        a = float(ll[1])
        p = float(ll[0])

        c.append(- a * math.sin(p))
        s.append(  a * math.cos(p))
        # c.append(float(ll[1]))
        # p.append(float(ll[0]))

        j = j + 1

print("c = ", end = "")
print(c)
print("s = ", end = "")
print(s)
