#!/usr/bin/env python

import sys, time
import Dominion
import Interop

specs = sys.argv[1:]

deck = Dominion.Deck(specs)

resultbatch = Dominion.ResultBatch()
decks = {}
modifs = []

start = time.time()
delay = 0.1
try:
    while True:
        resultbatch.base.accumulate(Dominion.Hand(deck).play())
        for m in modifs:
            resultbatch.accumulate(m, Dominion.Hand(decks[m]).play())
        now = time.time()
        if now - start > delay:
            start = now
            Interop.send(sys.stdout, resultbatch)
            modifs = Interop.recv(sys.stdin)
            for m in modifs:
                if m not in decks:
                    d = deck.clone()
                    for mod in m:
                        d.applyModif('+' + mod)
                    decks[m] = d
            resultbatch.reset()
except IOError, e:
    if e.errno != 32:
        raise e
except KeyboardInterrupt:
    pass
