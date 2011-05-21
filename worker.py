#!/usr/bin/env python

import sys, time
import Dominion
import Modifs
import Interop

specs = sys.argv[1:]

deck = Dominion.Deck(specs)

resultbatch = Dominion.ResultBatch(Modifs.MODIFS)
decks = {}
for m in Modifs.MODIFS:
    decks[m] = deck.clone()
    decks[m].applyModif(m)

start = time.time()
delay = 0.5
while True:
    resultbatch.base.accumulate(Dominion.Hand(deck).play())
    for m in Modifs.MODIFS:
        resultbatch.modif[m].accumulate(Dominion.Hand(decks[m]).play())
    now = time.time()
    if now - start > delay:
        start = now
        Interop.send(sys.stdout, resultbatch)
        resultbatch.reset()
