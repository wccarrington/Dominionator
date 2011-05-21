#!/usr/bin/env python

import sys, subprocess
import Dominion
import Interop
import Modifs

specs = sys.argv[1:]

p = subprocess.Popen(
    ["worker.py"]+specs,
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE)

resultbatch = Dominion.ResultBatch(Modifs.MODIFS)

try:
    while True:
        resultbatch.add(Interop.recv(p.stdout))

        sys.stdout.write("[H[2J")
        basesum = resultbatch.base.summary()
        print "%-22s: %s" % ("base:", basesum)
        sums = {}
        for m,hist in resultbatch.modif.items():
            sums[m] = hist.summary().sub(basesum)
        for m in sorted(sums.keys(), key=lambda m: sums[m].money+sums[m].buys, reverse=False):
            print "%-22s: %s" % (m, sums[m])

except KeyboardInterrupt:
    pass

p.send_signal(2)

print p.wait()
