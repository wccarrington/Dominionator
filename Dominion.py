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

#Static Cards
Card("Copper",      0, money=1, ismoney=True)
Card("Silver",      3, money=2, ismoney=True)
Card("Gold",        6, money=3, ismoney=True)
Card("Estate",      2, ispoints=True) # 1 point
Card("Duchy",       5, ispoints=True) # 3 points
Card("Province",    8, ispoints=True) # 6 points

#Dominion
Card("Adventurer",  6) # reveal and discard non-treasure until you have get two treasures, put the treasure in hand
Card("Bureaucrat",  4, money=3, buys=1) # effectively, gain a silver, put on top of deck. other players reveal victory card from hand and put on deck, or a victory card-less hand
Card("Cellar",      2, actions=1) # discard n cards to draw n cards
Card("Chancellor",  3, money=2)
Card("Chapel",      2) # discard 4
Card("CouncilRoom", 5, draws=4, buys=1)
Card("Feast",       4, money=5) # trash to gain a card up to cost 5
Card("Festival",    5, actions=2, buys=1, money=2)
Card("Garden",      4, ispoints=True) # 1 point per 10 cards
Card("Laboratory",  5, draws=2, actions=1)
Card("Library",     5) # draw to 7 card in hand
Card("Market",      5, draws=1, actions=1, buys=1, money=1)
Card("Militia",     4, money=2)
Card("Mine",        5) # replace one copper with silver, or one silver with gold, stays in hand
Card("Moat",        2, draws=2)
Card("Moneylender", 4) # trash a copper for +3 money
Card("Remodel",     4) # trash a card, gain a card costing up to 2 more
Card("Smithy",      4, draws=3)
Card("Spy",         4, draws=1, actions=1)
Card("Thief",       4)
Card("ThroneRoom",  4) # choose an action card, it takes effect twice
Card("Village",     3, actions=2, draws=1)
Card("Witch",       5, draws=2)
Card("Woodcutter",  3, buys=1, money=2)
Card("Workshop",    3) # gain a card up to cost 4

#Intrigue
Card("Baron",         4, buys=1) #discard and estate for +4 money, otherwise gain an estate
Card("Bridge",        4, buys=1, money=1) #everything is one cheaper
Card("Consiprator",   4, money=2) #if you've played 3 or more actions(including this one): +1 card, +1 action
Card("Coppersmith",   4) # 1 money per copper this turn
Card("Courtyard",     2, draws=3) #special: put one card on deck
Card("Duke",          5) #worth 1 point per duchy
Card("GreatHall",     3, draws=1, actions=1, ispoints=True) #1 point
Card("Harem",         6, money=2, ismoney=True, ispoints=True) # 2 points
Card("Ironworks",     4, money=4, buys=1) #effectively, if you get an actions-> +1 action, treasure-> +1 money, victory -> +1 card
Card("Masquerade",    3, draws=2) #all players pass a card to left, then may trash one
Card("MiningVillage", 4, draws=1, actions=2) #may trash for +2 money
Card("Minion",        5, actions=1) #+2 money or (discard your hand and +4 cards, and every other player with 5 or more card discards them and draws 4)
Card("Nobles",        6, ispoints=True) #+3 cards or +2 actions, 2 points
Card("Pawn",          2, draws=1, actions=1, buys=1, money=1) #pick 2
Card("Saboteur",      5) #each player reveals cards until one costs 3 or more, trash, and get a card costing at most 2 less
Card("Scout",         4, actions=1) #reveal top 4 cards of deck, all victory points go into hand, others go onto deck in any order
Card("SecretChamber", 2) #discard any number of cards, +1 per card discarded. when attacked, +2 card, then may put 2 cards from your hand on your deck
Card("Shanty Town",   3, actions=2) #reveal hand, +2 cards if no actions in it
Card("Steward",       3, draws=2, money=2) #trash 2, choose one
Card("Swindler",      3, money=2) #each other player trashes the top card of his deck, and gains a card with the same cost you choose
Card("Torturer",      5, draws=3) #everyone chooses one: discard 2 cards, or gain a curse
Card("TradingPost",  5) #Trash 2 cards, gain a silver in your hand
Card("Tribute",       5) #Player to your left reveals top 2 cards of deck, for each: action-> +2 actions, treasuer-> +2 money, victory-> +2 cards
Card("Upgrade",       5, draws=1, actions=1) #Trash a card, gain a card costing exactly 1 more
Card("WishingWell",   3, draws=1, actions=1) #name a card, reveal top of deck, if is named, put in hand

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
        self.purchaseSet = set()

    def accumulate(self, result):
        self.n += 1
        mapinc(self.money,   result.money)
        mapinc(self.buys,    result.buys)
        mapinc(self.actions, result.actions)
        mapinc(self.used,    result.used)
        self.purchaseSet.add((result.money, result.buys))

    def add(self, resulthist):
        self.n += resulthist.n
        mapadd(self.money,   resulthist.money)
        mapadd(self.buys,    resulthist.buys)
        mapadd(self.actions, resulthist.actions)
        mapadd(self.used,    resulthist.used)
        self.purchaseSet |= resulthist.purchaseSet

    def summary(self):
        return Summary(self.n,
            mapavg(self.money),
            mapavg(self.buys),
            mapavg(self.actions),
            mapavg(self.used))

class Summary:
    def __init__(self, n, money, buys, actions, used):
        self.n = n
        self.money = money
        self.buys = buys
        self.actions = actions
        self.used = used
    def __str__(self):
        return "money %+6.2f buys %+6.2f actions %+6.2f used %+6.2f (%i trials)" % (
            self.money, self.buys, self.actions, self.used, self.n)
    def sub(self, other):
        return Summary(self.n,
            self.money - other.money,
            self.buys - other.buys,
            self.actions - other.actions,
            self.used - other.used)

class ResultBatch:
    def __init__(self):
        self.reset()

    def add(self, resultbatch):
        self.base.add(resultbatch.base)
        for m,hist in resultbatch.modif.items():
            self.addhist(m, hist)

    def addhist(self, m, hist):
        if m not in self.modif:
            self.modif[m] = ResultHist()
        self.modif[m].add(hist)

    def accumulate(self, m, result):
        if m not in self.modif:
            self.modif[m] = ResultHist()
        self.modif[m].accumulate(result)

    def reset(self):
        self.base = ResultHist()
        self.modif = dict()

def getAllCombinations(cards, maxnum):
    if maxnum == 1:
        return [(c,) for c in cards]
    subcomb = getAllCombinations(cards, maxnum-1)
    ret = []
    for c in cards:
        for comb in subcomb:
            ret += (c) + comb
    return ret

def combinationCost(comb):
    return sum(getattr(Cards, c).cost for c in comb)

def possibleModifs(purchaseSet, cards):
    ret = set()
    moneyPerBuy = {}
    for money, buys in purchaseSet:
        if money > moneyPerBuy.get(buys, -1):
            moneyPerBuy[buys] = money
    allCombinations = getAllCombinations(cards, max(moneyPerBuy.keys()))
    for buys, money in moneyPerBuy.items():
        for comb in allCombinations:
            if len(comb) > buys:
                continue
            if combinationCost(comb) <= money:
                ret.add(comb)
    return ret
            
