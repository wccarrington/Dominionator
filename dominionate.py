#!/usr/bin/env python

import sys, subprocess
import Dominion
import Interop
import Modifs
import curses
from collections import defaultdict

cards = sys.argv[1:]

deck = defaultdict(lambda: 0, {'Copper': 7, 'Estate':3})

if len(cards) != 10:
    print 'You need exactly 10 cards to play Dominion.'
    sys.exit(1)
    
subprocesses = 2

workers = []

def start_workers(deck, cards):
    global workers
    specs = []
    for k,v in deck.items():
        specs.append(str(k) + '=' + str(v))
    workers = [subprocess.Popen(
        ["./worker.py"]+specs,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE) for x in xrange(subprocesses)]

start_workers(deck, cards)

resultbatch = Dominion.ResultBatch(Modifs.MODIFS)

def showdeck(deck):
    specs = [str(k) + '=' + str(v) for k,v in deck.items()]
    maxlength = max(len(x) for x in specs)+4
    for n, s in enumerate(sorted(specs)):
        window.addstr(n, cols-maxlength, s)

running = True

inputstate = 'main'

numbers = [ord(str(x)) for x in [1,2,3,4,5,6,7,8,9,0]]

try:
    window = curses.initscr()
    rows, cols = window.getmaxyx()
    window.timeout(0)

    while running:
        for w in workers:
            resultbatch.add(Interop.recv(w.stdout))

        c = window.getch()
        if inputstate == 'main':
            if c == ord('q'):
                running = False
            elif c == ord('a'):
                inputstate = 'add'
        elif inputstate == 'add':
            if c in numbers:
                n = numbers.index(c)
                deck[cards[n]] = deck[cards[n]] + 1
                inputstate = 'main'
            if c == ord('w'):
                deck['Copper'] = deck['Copper'] + 1
                inputstate = 'main'
            if c == ord('e'):
                deck['Silver'] = deck['Silver'] + 1
                inputstate = 'main'
            if c == ord('r'):
                deck['Gold'] = deck['Gold'] + 1
                inputstate = 'main'
            if c == ord('s'):
                deck['Estate'] = deck['Estate'] + 1
                inputstate = 'main'
            if c == ord('d'):
                deck['Duchy'] = deck['Duchy'] + 1
                inputstate = 'main'
            if c == ord('f'):
                deck['Province'] = deck['Province'] + 1
                inputstate = 'main'
            if c == ord('c'):
                inputstate = 'main'
        window.erase()
        window.move(0,0)
        if inputstate == 'main':
            basesum = resultbatch.base.summary()
            window.addstr("%-22s: %s" % ("base:", basesum), curses.A_REVERSE)
            sums = {}
            for m,hist in resultbatch.modif.items():
                sums[m] = hist.summary().sub(basesum)
            for n, m in enumerate(sorted(sums.keys(), key=lambda m: sums[m].money+sums[m].buys, reverse=False)[-rows+2:]):
                window.addstr(n+1, 0, "%-22s: %s" % (m, sums[m]))
            window.addstr(rows-1, 0, "[A]dd Card  [Q]uit", curses.A_REVERSE)
            showdeck(deck)
        elif inputstate == 'add':
            window.addstr(0,0, "Add a card")
            for n, card in enumerate(cards):
                window.addstr(n+1, 0, "%i: %s" % ((n+1) % 10, card))
            window.addstr(12, 0, "W: Copper")
            window.addstr(13, 0, "E: Silver")
            window.addstr(14, 0, "R: Gold")
            window.addstr(16, 0, "S: Estate")
            window.addstr(17, 0, "D: Duchy")
            window.addstr(18, 0, "F: Province")
            window.addstr(20, 0, "C: Cancel")
        window.refresh()
except KeyboardInterrupt:
    pass
finally:
    curses.endwin()

    for w in workers:
        w.send_signal(2)
        print w.wait()
