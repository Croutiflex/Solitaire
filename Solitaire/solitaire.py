import pygame as pg
from properties import *
from card import *
from utils import *
import random

# position des cartes
y1 = cardH + 2*space3
hiddenPilePos = [(space4 + (cardW + space3)*i, y1) for i in range(7)]
pilePos = [(hiddenPilePos[i][0], hiddenPilePos[i][1] + i*space1) for i in range(7)]
acePilePos = [(W - space4 - cardW - i*(space3 + cardW), space3) for i in range(4)]
handPos = (space4 + cardW + space2, space3)

# pioche
back = pg.image.load(cardsFolder + "back.png")
allCards = [Card(i+1, back, cardSize) for i in range(52)]

class Solitaire():
	def __init__(self):
		# self.backgroundColor = randomColor(high=200)
		self.background = pg.transform.smoothscale(pg.image.load("res/fond1.png"), screenSize)
		self.cheatEnabled = False
		self.isWon = False
		for c in allCards:
			c.hide()
			c._layer = 0
		self.deck = CardPile("deck", (space4, space3), cards=allCards)
		self.deckHL = HighLightRect(white, cardW+2*space5, cardH+2*space5, pos=self.deck.cards[0].rect.center)
		self.reserve = []
		self.hand = CardPile3("hand", handPos, offset=(space3, 0), limit=1)
		# piles
		self.hiddenPiles = [CardPile2("hidden", p, offset=(0, space1)) for p in hiddenPilePos]
		self.piles = [CardPile3("normal", p, offset=(0, space2)) for p in pilePos]
		self.acePiles = [CardPile4("ace", p) for p in acePilePos]
		self.activePiles = self.acePiles + self.piles
		# sons
		self.sounds = [pg.mixer.Sound(soundResPath+"carte"+str(i)+".wav") for i in range(1,10)]
		self.playlist1 = [self.sounds[1], self.sounds[2], self.sounds[3]]
		self.defeatSound = pg.mixer.Sound(soundResPath+"pwapwa.wav")
		self.victorySound = pg.mixer.Sound(soundResPath+"tinting.wav")
		# détection de la défaite
		self.noMoreDeckMoves = False
		self.lastDeckLen = len(self.deck)
		# démarrage de la distribution
		self.deal()

	def toggleCheat(self):
		if self.cheatEnabled:
			self.cheatEnabled = False
			print("Cheat disabled")
		else:
			self.cheatEnabled = True
			print("Cheat enabled")

	# redistribuer
	def reset(self):
		for c in allCards:
			c._layer = 0
		for p in self.activePiles + self.hiddenPiles + [self.hand]:
			p.empty()
		for c in allCards:
			c.hide()
		self.deck = CardPile("deck", (space4, space3), cards=allCards)
		self.deal()

	def deal(self):
		self.phase = DEAL
		random.shuffle(self.deck.cards)
		self.movingCard = self.deck.pick()
		self.movingCard.show()
		self.dealA = 0
		self.dealB = 0
		def onDone():
			self.piles[0].add(self.movingCard)
			self.movingCard = None
			playRandomSound(self.playlist1)
		self.movingCard.animate(self.piles[0].nextCardPos, onDone)
		# pour le déplacement des cartes
		self.pileUnderMouse = None
		self.movingPile = None
		self.originPile = None

	def isMoveAllowed(self, A: CardPile, B: CardPile): # règles de pose : peut-on poser les cartes de la pile A sur la pile B?
		if self.cheatEnabled:
			return True
		if B.type == "ace":
			if len(A) > 1:
				return False
			a = A.cards[0]
			if len(B) == 0:
				return a.value == 1
			b = B.cards[-1]
			return a.color == b.color and a.value == b.value + 1
		elif B.type == "normal":
			a = A.cards[0]
			if len(B) == 0:
				return a.value == 13
			b = B.cards[-1]
			return a.isRed == b.isBlack and a.value == b.value - 1
		return False

	def checkDefeat(self, isDeckUnchanged: bool):
		if self.noMoreDeckMoves and isDeckUnchanged:
			# check for moves on the board
			for A in self.piles:
				if len(A) == 0:
					continue
				for B in self.piles:
					if A != B and A.cards[0].value != 13 and self.isMoveAllowed(A, B):
						print("move possible : ", str(A.cards[0]), " sur ", str(B.getNext()))
						return False
				dummyPile = CardPile2("dummy", (0,0))
				dummyPile.add(A.getNext(), updatePos=True)
				for B in self.acePiles:
					if self.isMoveAllowed(dummyPile, B):
						print("move possible : ", str(dummyPile.cards[0]), " sur ", str(B.getNext()))
						return False
			return True
		# check for deck moves
		playableCards = []
		i = 2
		while i < len(self.reserve):
			playableCards.append(self.reserve[i])
			i += 3
		if len(self.reserve)%3 != 0:
			playableCards.append(self.reserve[-1])
		# print("playableCards : ", [str(c) for c in playableCards])
		for c in playableCards:
			A = CardPile2("dummy", (0,0))
			A.add(c, updatePos=True)
			for B in self.activePiles:
				if self.isMoveAllowed(A, B):
					print("move possible : pioche sur ", str(B.getNext()))
					self.noMoreDeckMoves = False
					return False
		# aucun move trouvé
		self.noMoreDeckMoves = True
		return False

	def checkVictory(self):
		if len(self.deck) == 0 and len(self.hand) == 0 and len(self.reserve) == 0:
			for p in self.hiddenPiles:
				if len(p) > 0:
					return False
			self.isWon = True
			return True

	def pioche(self):
		# print("deck : ", len(self.deck), ", réserve : ", len(self.reserve), ", main : ", len(self.hand))
		if self.checkVictory():
			print("Victoire!")
			self.phase = WIN
			self.lastStackingPileIndex = 6
			self.stackUp()
			return
		if len(self.deck) == 0 and len(self.hand) == 0:
			if self.checkDefeat(self.lastDeckLen == len(self.reserve)):
				print("Game Over!")
				self.defeatSound.play()
				self.phase = END
				return
			# si la pioche et la main sont vides, remettre la réserve dans le deck
			for c in self.reserve[::-1]:
				c.hide()
				c._layer = 0
				self.deck.add(c)
			self.reserve = []
			self.lastDeckLen = len(self.deck)
		else :
			# vider la main dans la réserve
			self.reserve += self.hand.cards
			self.hand.empty()
			# piocher n cartes
			self.sounds[8].play()
			for i in range(min(3, len(self.deck))):
				c = self.deck.pick()
				c.show()
				self.hand.add(c)

	# sur quelle pile As c peut-elle aller?
	def getAceTarget(self, c):
		A = CardPile2("dummy", (0,0))
		A.add(c, updatePos=True)
		for B in self.acePiles:
			if self.isMoveAllowed(A, B):
				return B
		return None

	# logique de rangement des cartes (animation victoire)
	def stackUp(self):
		# find next stacking move
		nextStackingPile = None
		nextStackingTarget = None
		i = self.lastStackingPileIndex + 1
		emptyPiles = set()
		searching = True
		nloops = 0
		while searching:
			if i == 7:
				i = 0
				nloops += 1
				if nloops > 2:
					print("This should not happen!")
					searching = False
			if len(self.piles[i]) > 0:
				target = self.getAceTarget(self.piles[i].getNext())
				if target != None: # next move found
					nextStackingPile = self.piles[i]
					nextStackingTarget = target
					self.lastStackingPileIndex = i
					searching = False
			else:
				if self.piles[i] not in emptyPiles:
					emptyPiles.add(self.piles[i])
					if len(emptyPiles) == 7: # stacking is done
						searching = False
			i += 1
		# stack next card
		if nextStackingPile == None: # fin de l'animation
			self.victorySound.play()
			self.phase = END
			return
		self.movingCard = nextStackingPile.pick()
		def f():
			nextStackingTarget.add(self.movingCard)
			self.movingCard = None
			playRandomSound(self.playlist1)
		self.movingCard.animate(nextStackingTarget.pos, onDone=f, duration=slideTime3)

	# renvoie True si la partie est terminée
	def leftClick(self):
		if self.pileUnderMouse == None or self.phase != GAME:
			return
		if self.pileUnderMouse.type == "deck":
			self.pioche()
			return
		self.movingPile = self.pileUnderMouse.pickSelected()
		if self.movingPile == None:
			return
		self.sounds[6].play()
		self.movingPile.followMouse()
		self.originPile = self.pileUnderMouse
		return

	def leftRelease(self):
		if self.phase != GAME or self.movingPile == None:
			return
		if self.pileUnderMouse != None and self.pileUnderMouse != self.originPile and self.isMoveAllowed(self.movingPile, self.pileUnderMouse):
			# on pose les cartes sur la nouvelle pile
			self.sounds[1].play()
			for c in self.movingPile.cards:
				self.pileUnderMouse.add(c)
			if self.originPile.type == "normal" and len(self.originPile) == 0: # découvrir une carte si la pile d'origine (non as) est vide
				self.discover(self.originPile)
			elif self.originPile.type == "hand" and len(self.hand) == 0: # si on vide la main, ajouter la carte suivante
				c = self.deck.pick()
				if c != None:
					c.show()
					self.hand.add(c)
		else: # retour à l'envoyeur
			for c in self.movingPile.cards:
				self.originPile.add(c)
		self.movingPile.unfollowMouse()
		self.movingPile = None
		self.originPile = None

	# renvoie True si la partie est terminée
	def rightClick(self):
		if self.pileUnderMouse == None or self.phase != GAME or self.movingCard != None:
			return
		dummyPile = CardPile2("dummy", (0,0))
		A = self.pileUnderMouse
		if len(A) == 0:
			return
		match A.type:
			case "deck":
				return
			case "normal":
				L = A.peekSelection()
				if len(L) != 1:
					return
				dummyPile.add(L[0], updatePos=True)
			case _:
				dummyPile.add(A.getNext(), updatePos=True)
				if len(dummyPile) == 0:
					return
		moves = []
		for B in self.activePiles:
			if B != A and self.isMoveAllowed(dummyPile, B):
				moves.append(B)
		# sort moves?
		for dest in moves: # Execute first move
			self.movingCard = A.pick()
			self.sounds[0].play()
			if A.type == "normal" and len(A) == 0: # découvrir une carte si la pile d'origine (non as) est vide
				self.discover(A)
			elif A.type == "hand":
				self.hand.drawables.remove(self.hand.HL)
				if len(self.hand) == 0: # si on vide la main, ajouter la carte suivante
					c = self.deck.pick()
					if c != None:
						c.show()
						self.hand.add(c)
			def f1():
				dest.add(self.movingCard)
				self.movingCard = None
			self.movingCard.animate(dest.nextCardPos, onDone=f1, duration=slideTime2)
			return
		return

	def discover(self, pile):
		hp = self.hiddenPiles[self.piles.index(pile)]
		c = hp.pick()
		if c == None:
			return
		c.show()
		pile.add(c, updatePos=True) # la carte change de pile mais ne bouge pas

	def update(self):
		match self.phase:
			case 0: # distribution
				if self.movingCard == None: # pas de carte qui bouge
					if len(self.deck) == 24: # fin de distribution
						self.phase = GAME
					else: # distribuer la carte suivante
						self.movingCard = self.deck.pick()
						self.dealB += 1
						if self.dealB == 7:
							self.dealA += 1
							self.dealB = self.dealA
							self.movingCard.show()
							def f1():
								self.piles[self.dealB].add(self.movingCard)
								self.movingCard = None
								playRandomSound(self.playlist1)
							self.movingCard.animate(self.piles[self.dealB].nextCardPos, f1)
						else:
							def f2():
								self.hiddenPiles[self.dealB].add(self.movingCard)
								self.movingCard = None
								playRandomSound(self.playlist1)
							self.movingCard.animate(self.hiddenPiles[self.dealB].nextCardPos, f2)
				else:
					self.movingCard.update()
			case 1: # jeu
				if self.movingPile != None:
					self.movingPile.update()
				if self.movingCard != None:
					self.movingCard.update()
					return
				self.pileUnderMouse = None
				if self.deckHL.rect.collidepoint(pg.mouse.get_pos()):
					self.pileUnderMouse = self.deck
				else:
					for p in self.activePiles + [self.hand]:
						if p.update():
							self.pileUnderMouse = p
			case 2: # animation victoire
				if self.movingCard != None:
					self.movingCard.update()
				else:
					self.stackUp()

	def draw(self, screen):
		screen.blit(self.background, (0,0))
		if self.pileUnderMouse == self.deck:
			self.deckHL.draw(screen)
		for p in self.acePiles + [self.hand, self.deck]:
			p.draw(screen)
		for i in range(7):
			self.hiddenPiles[i].draw(screen)
			self.piles[i].draw(screen)
		if self.movingCard != None:
			self.movingCard.draw(screen)
		if self.movingPile != None:
			if self.pileUnderMouse != None and len(self.pileUnderMouse) == 0:
				self.pileUnderMouse.drawHL(screen)
			self.movingPile.draw(screen)