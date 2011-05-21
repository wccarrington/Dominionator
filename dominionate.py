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
        print "%-22s: %s" % ("base:", resultbatch.base.summary())
        for m,hist in sorted(resultbatch.modif.items()):
            print "%-22s: %s" % (m, hist.summary())
except KeyboardInterrupt:
    pass

p.send_signal(2)

print p.wait()
