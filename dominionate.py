#!/usr/bin/env python

import sys, subprocess
import Dominion
import Interop
import Modifs
import curses

window = curses.initscr()
rows, cols = window.getmaxyx()

specs = sys.argv[1:]

subprocesses = 2

workers = [subprocess.Popen(
           ["./worker.py"]+specs,
           stdin = subprocess.PIPE,
           stdout = subprocess.PIPE) for x in xrange(subprocesses)]

resultbatch = Dominion.ResultBatch(Modifs.MODIFS)

def showdeck(specs):
    maxlength = max(len(x) for x in specs)+4
    for n, s in enumerate(sorted(specs)):
        window.addstr(n, cols-maxlength, s)

try:
    while True:
        for w in workers:
            resultbatch.add(Interop.recv(w.stdout))

        window.erase()
        window.move(0,0)
        basesum = resultbatch.base.summary()
        window.addstr("%-22s: %s" % ("base:", basesum), curses.A_REVERSE)
        sums = {}
        for m,hist in resultbatch.modif.items():
            sums[m] = hist.summary().sub(basesum)
        for n, m in enumerate(sorted(sums.keys(), key=lambda m: sums[m].money+sums[m].buys, reverse=False)[-rows+2:]):
            window.addstr(n+1, 0, "%-22s: %s" % (m, sums[m]))
        window.addstr(rows-1, 0, "[A]dd Card", curses.A_REVERSE)
        showdeck(specs)
        window.refresh()
except KeyboardInterrupt:
    pass
finally:
    curses.endwin()

    for w in workers:
        w.send_signal(2)
        print w.wait()
