#!/usr/bin/env python

import random

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
Card("Workshop",    3, money=4, buys=1) # effectively
Card("Bureaucrat",  4, money=3, buys=1) # effectively
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
    def __init__(self, specs=[]):
        self.cards = []
        for spec in specs:
            cardname,number = spec.split('=')
            assert hasattr(Cards, cardname), cardname
            assert number > 0
            for i in xrange(int(number)):
                self.cards.append(getattr(Cards, cardname))
        self.shuffle()

    def clone(self):
        d = Deck()
        d.cards = self.cards[:]
        return d

    def applyModif(self, modif):
        if modif[0] == '+':
            for cardname in modif[1:].split(','):
                assert hasattr(Cards, cardname), cardname
                self.cards.append(getattr(Cards, cardname))
        else:
            assert False, "bad modif: "+modif

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

def mapinc(d, k, v=1):
    d[k] = d.get(k,0)+v

def mapadd(d1, d2):
    for k,v in d2.items():
        mapinc(d1, k, v)

def mapavg(d):
    return float(sum([k*v for k,v in d.items()])) / sum(d.values())

class ResultHist:
    def __init__(self):
        self.n = 0
        self.money = {}
        self.buys = {}
        self.actions = {}
        self.used = {}

    def accumulate(self, result):
        self.n += 1
        mapinc(self.money,   result.money)
        mapinc(self.buys,    result.buys)
        mapinc(self.actions, result.actions)
        mapinc(self.used,    result.used)

    def add(self, resulthist):
        self.n += resulthist.n
        mapadd(self.money,   resulthist.money)
        mapadd(self.buys,    resulthist.buys)
        mapadd(self.actions, resulthist.actions)
        mapadd(self.used,    resulthist.used)

    def summary(self):
        return "money %6.2f buys %6.2f actions %6.2f used %6.2f (%i trials)" % (
            mapavg(self.money),
            mapavg(self.buys),
            mapavg(self.actions),
            mapavg(self.used),
            self.n)

class ResultBatch:
    def __init__(self, modifs):
        self.base = ResultHist()
        self.modif = dict([(m,ResultHist()) for m in modifs])

    def add(self, resultbatch):
        self.base.add(resultbatch.base)
        for m,hist in resultbatch.modif.items():
            self.modif[m].add(hist)

    def reset(self):
        self.base = ResultHist()
        for m in self.modif.keys():
            self.modif[m] = ResultHist()
