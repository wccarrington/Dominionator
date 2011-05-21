#!/usr/bin/env python

import sys, time, math
import Dominion

def stats(numbers):
    mean = float(sum(numbers))/len(numbers)
    dev = math.sqrt(sum([(mean-x)**2 for x in numbers])/len(numbers))
    return mean, dev

def summarize(results):
    out = [
        "Trials: %i" % len(results),
        "Money:   mean %6.3f, stddev %6.3f" % stats([r.money   for r in results]),
        "Buys:    mean %6.3f, stddev %6.3f" % stats([r.buys    for r in results]),
        "Actions: mean %6.3f, stddev %6.3f" % stats([r.actions for r in results]),
        "Used:    mean %6.3f, stddev %6.3f" % stats([r.used    for r in results]),
    ]
    print '\n'.join(out)

def continuous(deck, delay = 0.15):
    last = time.time()
    results = []
    sys.stdout.write("[2J[H")
    sys.stdout.flush()
    try:
        while True:
            results.append(Dominion.Hand(deck).play())
            now = time.time()
            if now - last > delay:
                last = now
                sys.stdout.write("[H")
                summarize(results)
    except KeyboardInterrupt: pass

def main():
    import optparse
    p = optparse.OptionParser()
    p.add_option('-n', '--num', type='int')
    p.add_option('-s', '--summary', action='store_true')
    p.add_option('-c', '--continuous', action='store_true')
    p.set_defaults(num=1, summary=False)

    opts, specs = p.parse_args()

    deck = Dominion.Deck(specs)

    if opts.continuous:
        continuous(deck)
    else:
        if not opts.summary:
            print "\tmoney\tbuys\tactions\tused"
        results = []
        for i in xrange(opts.num):
            result = Dominion.Hand(deck, i).play()
            if opts.summary:
                results.append(result)
            else:
                print "%i\t%i\t%i\t%i\t%i" % (i, result.money, result.buys, result.actions, result.used)
        if opts.summary:
            summarize(results)

if __name__ == '__main__':
    main()
