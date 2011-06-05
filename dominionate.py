#!/usr/bin/env python

import sys, subprocess
import Dominion
import Interop
import curses
from collections import defaultdict

cards = sorted(sys.argv[1:])

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

def stop_workers():
    global workers
    for w in workers:
        w.send_signal(2)
        w.wait()
    workers = []

start_workers(deck, cards)

resultbatch = Dominion.ResultBatch()

def showdeck(deck):
    specs = sorted([str(k) + '=' + str(v) for k,v in deck.items()])
    maxlength = max(len(x) for x in specs)+4
    for n, s in enumerate(sorted(specs)):
        window.addstr(n, cols-maxlength, s)

def addToDeck(deck, card):
    deck[card] = deck[card] + 1

def removeFromDeck(deck, card):
    if deck[card] > 0:
        deck[card] = deck[card] - 1
    if deck[card] == 0:
        del deck[card]

running = True

inputstate = 'main'

numbers = [ord(str(x)) for x in [1,2,3,4,5,6,7,8,9,0]]

cardchoices = dict(zip(numbers, cards) + [(ord('w'), 'Copper'), (ord('e'), 'Silver'), (ord('r'), 'Gold'),
                                          (ord('s'), 'Estate'), (ord('d'), 'Duchy'), (ord('f'), 'Province')])

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
            elif c == ord('r'):
                inputstate = 'remove'
        elif inputstate == 'add':
            if c in cardchoices:
                addToDeck(deck, cardchoices[c])
                inputstate = 'main'
            if c == ord('c'):
                inputstate = 'main'
        elif inputstate == 'remove':
            if c in cardchoices:
                removeFromDeck(deck, cardchoices[c])
                inputstate = 'main'
            if c == ord('c'):
                inputstate = 'main'
        window.erase()
        window.move(0,0)
        if inputstate == 'main':
            basesum = resultbatch.base.summary()
            window.addstr(0, 0, "%-22s: %s" % ("base:", basesum), curses.A_REVERSE)
            window.addstr(1, 0, str(resultbatch.base.purchaseset))
            sums = {}
            for m,hist in resultbatch.modif.items():
                sums[m] = hist.summary().sub(basesum)
            for n, m in enumerate(sorted(sums.keys(), key=lambda m: sums[m].money+sums[m].buys, reverse=False)[-rows+2:]):
                window.addstr(n+1, 0, "%-22s: %s" % (m, sums[m]))
            window.addstr(rows-1, 0, "[A]dd Card  [R]emove Card  [Q]uit", curses.A_REVERSE)
            showdeck(deck)
        elif inputstate == 'add':
            window.addstr(0,0, "Add a card")
            for n, card in enumerate(cards):
                window.addstr(n+1, 0, "%i: %s" % ((n+1) % 10, card))
            base = len(cards)
            window.addstr(base+2, 0, "W: Copper")
            window.addstr(base+3, 0, "E: Silver")
            window.addstr(base+4, 0, "R: Gold")
            window.addstr(base+6, 0, "S: Estate")
            window.addstr(base+7, 0, "D: Duchy")
            window.addstr(base+8, 0, "F: Province")
            window.addstr(base+10, 0, "C: Cancel")
        elif inputstate == 'remove':
            for n, card in enumerate(cards):
                window.addstr(n+1, 0, "%i: %s" % ((n+1) % 10, card))
            base = len(cards)
            window.addstr(base+2, 0, "W: Copper")
            window.addstr(base+3, 0, "E: Silver")
            window.addstr(base+4, 0, "R: Gold")
            window.addstr(base+6, 0, "S: Estate")
            window.addstr(base+7, 0, "D: Duchy")
            window.addstr(base+8, 0, "F: Province")
            window.addstr(base+10, 0, "C: Cancel")
        window.refresh()
except KeyboardInterrupt:
    pass
finally:
    curses.endwin()

    stop_workers()
