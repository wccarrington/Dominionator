#!/usr/bin/env python

MODIFS = []

pairs = "Gold Silver Copper Estate Cellar Market Militia Mine Moat Remodel Smithy Village Woodcutter Workshop".split()

MODIFS = ["+%s,%s" % (a,b) for (a,b) in set([tuple(sorted((a,b))) for a in pairs for b in pairs])]

