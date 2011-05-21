#!/usr/bin/env python

import sys, subprocess
import Interop

specs = sys.argv[1:]

p = subprocess.Popen(
    ["worker.py"]+specs,
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE)

while True:
    resultbatch = Interop.recv(p.stdout)
    print resultbatch.base.n

p.send_signal(2)

print p.wait()
