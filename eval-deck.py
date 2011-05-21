#!/usr/bin/env python

import sys, random, math, time

class Cards:
    pass

sortkey = 0
class Card:
    def __init__(self, name, cost, actions=0, draws=0, money=0, buys=0, ismoney=False, ispoints=False):
        setattr(Cards, name, self)
        global sortkey
        self.sortkey = sortkey
        sortkey += 1
        self.name = name
        self.cost = cost
        self.actions = actions
        self.draws = draws
        self.money = money
        self.buys = buys
        self.ismoney = ismoney
        self.ispoints = ispoints
    def __str__(self): return self.name
    def __repr__(self): return self.name

Card("Copper",      0, money=1, ismoney=True)
Card("Silver",      3, money=2, ismoney=True)
Card("Gold",        6, money=3, ismoney=True)
Card("Estate",      2, ispoints=True)
Card("Duchy",       5, ispoints=True)
Card("Province",    8, ispoints=True)
Card("Garden",      4, ispoints=True)
Card("Cellar",      2, actions=1) # special; you should hang on to points to drop them here
Card("Chapel",      2)
Card("Moat",        2, draws=2)
Card("Chancellor",  3, money=2)
Card("Village",     3, actions=2, draws=1)
Card("Woodcutter",  3, buys=1, money=2)
Card("Feast",       4, money=5) # effectively
Card("Militia",     4, money=2)
Card("Moneylender", 4) # special: money = 3 if copper in hand, 0 otherwise
Card("Remodel",     4, money=2) # effectively
Card("Smithy",      4, draws=3)
Card("Spy",         4, draws=1, actions=1)
Card("Thief",       4)
Card("ThroneRoom",  4) # special, weird
Card("CouncilRoom", 5, draws=4, buys=1)
Card("Festival",    5, actions=2, buys=1, money=2)
Card("Laboratory",  5, draws=2, actions=1)
Card("Library",     5) # special: draws = 7-handsize
Card("Market",      5, draws=1, actions=1, buys=1, money=1)
Card("Mine",        5) # special: if have any copper or silver, money=2
Card("Witch",       5, draws=2)
Card("Adventurer",  6) # special, draw until you have get two treasure draws

class Deck:
    def __init__(self, specs):
        self.cards = []
        for spec in specs:
            cardname,number = spec.split('=')
            assert hasattr(Cards, cardname), cardname
            assert number > 0
            for i in xrange(int(number)):
                self.cards.append(getattr(Cards, cardname))
        self.shuffle()

    def candraw(self):
        return self.index < len(self.cards)

    def draw(self):
        assert self.candraw()
        card = self.cards[self.index]
        self.index += 1
        return card

    def shuffle(self):
        random.shuffle(self.cards)
        self.index = 0

class Hand:
    def __init__(self, deck, idx=None):
        self.hand = []

        self.deck = deck
        self.deck.shuffle()
        self.draw(5)

        self.idx = idx

        self.money = 0
        self.actions = 1
        self.buys = 1
        self.played = []

    def play(self):
        while True:
            card = self.chooseCard()
            if card is None: break
            self.playCard(card)
        return Result(self)

    def draw(self, n):
        if n <= 0: return
        for i in xrange(n):
            if self.deck.candraw():
                card = self.deck.draw()
                #print "Draw:",card
                self.hand.append(card)
            else:
                pass
                #print "Can't draw, deck exhausted."

    def chooseCard(self):
        for card in [Cards.Village, Cards.Market, Cards.Festival]:
            if card in self.hand:
                return card

        # TODO: heuristic: use extra actions first?

        if self.actions > 0:
            actions = filter(lambda c: not c.ismoney and not c.ispoints, self.hand)
            if len(actions) > 0:
                return random.choice(actions)

        for card in [Cards.Copper, Cards.Silver, Cards.Gold]:
            if card in self.hand:
                return card

        for card in [Cards.Estate, Cards.Garden, Cards.Duchy, Cards.Province]:
            if card in self.hand:
                return card

        return None

    def playCard(self, card):
        #print "Playing", card
        self.hand.remove(card)

        if card.ispoints:
            return
        if card.ismoney:
            self.money += card.money
            return

        self.actions -= 1

        self.actions += card.actions
        self.money += card.money
        self.buys += card.buys
        self.draw(card.draws)

        if card is Cards.Moneylender:
            if Cards.Copper in self.hand:
                self.hand.remove(Cards.Copper)
                self.money += 3

        if card is Cards.Library:
            self.draw(7-len(self.hand))

        if card is Cards.Mine and Cards.Copper in self.hand:
            self.hand.remove(Cards.Copper)
            self.hand.append(Cards.Silver)
        elif card is Cards.Mine and Cards.Silver in self.hand:
            self.hand.remove(Cards.Silver)
            self.hand.append(Cards.Gold)

        if card is Cards.Cellar:
            points = filter(lambda c: c.ispoints, self.hand)
            self.hand = filter(lambda c: not c.ispoints, self.hand)
            self.draw(len(points))

        if card is Cards.Adventurer:
            assert False, "fuck that shit"

    def __str__(self):
        return ' '.join([str(c) for c in sorted(self.hand, key=lambda c: c.sortkey)])

class Result:
    def __init__(self, hand):
        self.idx = hand.idx
        self.money = hand.money
        self.buys = hand.buys
        self.actions = hand.actions
        self.used = hand.deck.index
        self.decksize = len(hand.deck.cards)
    def __str__(self):
        return "Result money %2i, buys %i, actions %i, used %2d/%2d (%6.2f%%)" % (
            self.money, self.buys, self.actions, self.used, self.decksize, 100.*self.used/self.decksize)
    def oneline(self):
        return "%i\t%i\t%i\t%i\t%i" % (self.idx, self.money, self.buys, self.actions, self.used)
    HEADER = "\tmoney\tbuys\tactions\tused"

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
            results.append(Hand(deck).play())
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

    deck = Deck(specs)

    if opts.continuous:
        continuous(deck)
    else:
        if not opts.summary:
            print Result.HEADER
        results = []
        for i in xrange(opts.num):
            result = Hand(deck, i).play()
            if opts.summary:
                results.append(result)
            else:
                print result.oneline()
        if opts.summary:
            summarize(results)

if __name__ == '__main__':
    main()
