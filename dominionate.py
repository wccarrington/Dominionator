#!/usr/bin/env python

import sys, subprocess
import Dominion
import Interop
import Modifs
import curses
import os

window = curses.initscr()
rows, cols = window.getmaxyx()

specs = sys.argv[1:]

subprocesses = 2

workers = [subprocess.Popen(
           ["./worker.py"]+specs,
           stdin = subprocess.PIPE,
           stdout = subprocess.PIPE) for x in xrange(subprocesses)]

resultbatch = Dominion.ResultBatch(Modifs.MODIFS)

try:
    while True:
        for w in workers:
            resultbatch.add(Interop.recv(w.stdout))

#        sys.stdout.write("[H[2J")
        window.erase()
        window.move(0,0)
        basesum = resultbatch.base.summary()
        window.addstr("%-22s: %s" % ("base:", basesum))
        sums = {}
        for m,hist in resultbatch.modif.items():
            sums[m] = hist.summary().sub(basesum)
        for n, m in enumerate(sorted(sums.keys(), key=lambda m: sums[m].money+sums[m].buys, reverse=False)[-rows:]):
            window.move(n, 0)
            window.addstr("%-22s: %s" % (m, sums[m]))
        window.refresh()

finally:
    curses.endwin()

    for w in workers:
        w.send_signal(2)
        print w.wait()
