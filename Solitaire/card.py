import pygame as pg
from utils import *
from properties import *

class Card(SpriteWithTL):
	def __init__(self, Id, back, size):
		self.Id = Id
		self.imageFront = pg.transform.smoothscale(pg.image.load(cardsFolder + str(Id) + ".png"), size)
		self.imageBack = pg.transform.smoothscale(back, size)
		super().__init__(self.imageBack)
		self.hidden = True
		self.color = (Id-1)//13
		self.value = Id%13
		if self.value == 0:
			self.value = 13
		self.isRed = self.color%2 == 0
		self.isBlack = not self.isRed
		self.isFollowingMouse = False
		# print("création : ", str(self))

	def __str__(self):
		ret = ""
		match self.value:
			case 1:
				ret += "As"
			case 11:
				ret += "Valet"
			case 12:
				ret += "Dame"
			case 13:
				ret += "Roi"
			case _:
				ret += str(self.value)
		return ret + " de " + colorLabel[self.color]

	def hide(self):
		self.image = self.imageBack
		self.hidden = True

	def show(self):
		self.image = self.imageFront
		self.hidden = False

	def flip(self):
		if self.hidden:
			self.show()
		else:
			self.hide()

	# tell the card to start following the mouse
	def followMouse(self, relativePos=(0,0)):
		self.posToMouse = relativePos
		self.isFollowingMouse = True

	def unfollowMouse(self):
		self.isFollowingMouse = False

	def update(self):
		if self.isFollowingMouse:
			(x,y) = self.posToMouse
			(a,b) = pg.mouse.get_pos()
			self.rect.center = (x+a, y+b)
		else:
			super().update()

class CardPile(): # pile simple sans déroulement
	def __init__(self, type, pos, cards=[], moveCards=True, isQueue=False):
		self.cards = [c for c in cards]
		self.isQueue = isQueue
		self.pos = pos
		self.initialPos = pos
		self.nextCardPos = pos
		self.type = type
		if moveCards:
			for c in self.cards:
				c.move(pos)

	def __len__(self):
		return len(self.cards)

	def __str__(self):
		if len(self) == 0:
			return "[]"
		ret = "[" + str(self.cards[0])
		for c in self.cards[1:]:
			ret += ", "+str(c)
		ret += "]"
		return ret

	def add(self, card): # ajouter une carte
		card.move(self.pos)
		if self.isQueue:
			self.cards.insert(0,card)
		else:
			self.cards.append(card)

	def pick(self): # piocher la dernière carte
		if len(self) == 0:
			return None
		return self.cards.pop(-1)

	def getNext(self):
		if len(self) == 0:
			return None
		return self.cards[-1]

	def empty(self): # vider la pile
		self.cards = []
		self.pos = self.initialPos

	def draw(self, screen):
		if len(self) == 0:
			return
		self.cards[-1].draw(screen)

class CardPile2(CardPile): # pile déroulante sans interaction avec la souris
	def __init__(self, type, pos, offset=(0,0), cards=[]):
		super().__init__(type, pos, cards, moveCards=False)
		self.baseOffset = offset
		self.offset = offset
		self.maxLenBeforeShrinking = (screenBottom - cardH - self.pos[1])//self.baseOffset[1] if self.baseOffset[1] > 0 else 999999999
		self.nextCardPos = pos
		for c in self.cards:
			c.move(self.nextCardPos)
			self.nextCardPos = (self.nextCardPos[0] + offset[0], self.nextCardPos[1] + offset[1])
		self.drawables = pg.sprite.LayeredUpdates(self.cards)

	def reposition(self, moreCards):
		if self.offset[1] == 0:
			return
		offsetChanged = False
		if len(self) > self.maxLenBeforeShrinking: # si la pile dépasse
			self.offset = (self.offset[0], (screenBottom - cardH - self.pos[1])/len(self))
			offsetChanged = True
		elif not moreCards and len(self) <= self.maxLenBeforeShrinking: # si la pile ne dépasse plus
			self.offset = self.baseOffset
			offsetChanged = True
		if offsetChanged:
			# print("offset: ", self.offset, ", base: ", self.baseOffset)
			(x,y) = self.pos
			for c in self.cards[1:]:
				y += self.offset[1]
				c.move((x,y))

	def pick(self):
		c = super().pick()
		if c == None:
			return None
		if len(self) == 0:
			self.nextCardPos = self.pos
		else:
			self.reposition(False)
			self.nextCardPos = (self.cards[-1].rect.left + self.offset[0], self.cards[-1].rect.top + self.offset[1])
		self.drawables.remove(c)
		return c

	def add(self, card, updatePos=False):
		if updatePos: # repositionner la pile sur la nouvelle carte sans la bouger
			self.nextCardPos = card.rect.topleft
			self.pos = self.nextCardPos
			self.maxLenBeforeShrinking = (screenBottom - cardH - self.pos[1])//self.baseOffset[1] if self.baseOffset[1] > 0 else 999999999
		else:
			card.move(self.nextCardPos)
		self.nextCardPos = (self.nextCardPos[0] + self.offset[0], self.nextCardPos[1] + self.offset[1])
		self.cards.append(card)
		self.reposition(True)
		self.drawables.add(card)

	def empty(self):
		self.drawables.empty()
		super().empty()
		self.nextCardPos = self.pos

	def followMouse(self):
		x,y = 0,0
		(dx, dy) = self.offset
		for c in self.cards:
			c.followMouse((x,y))
			x += dx
			y += dy

	def unfollowMouse(self):
		for c in self.cards:
			c.unfollowMouse()

	def update(self):
		self.drawables.update()

	def draw(self, screen):
		self.drawables.draw(screen)


class CardPile3(CardPile2): # pile avec déroulement et sélection multiple
	def __init__(self, type, pos, offset=(0,0), cards=[], limit=None):
		# limit = nbre de cartes piochables max. (limit=1 -> seule la carte du dessus est piochable)
		super().__init__(type, pos, offset, cards)
		n = 0
		for c in self.cards:
			c._layer = n
			n += 2
		self.HL = HighLightRect(white, cardW+2*space5, cardH+2*space5)
		self.limit = limit
		if limit == None:
			self.collidables = pg.sprite.LayeredUpdates(self.cards)
		else:
			self.collidables = pg.sprite.LayeredUpdates(self.cards[-1*limit:])

	def updateCollidables(self):
		if self.limit == None:
			self.collidables = pg.sprite.LayeredUpdates(self.cards)
		else:
			self.collidables.empty()
			for i in range(min(len(self), self.limit)):
				self.collidables.add(self.cards[len(self)-i-1])

	def add(self, card, updatePos=False):
		if len(self) == 0:
			card._layer = 0
		else:
			card._layer = self.cards[-1]._layer + 2
		super().add(card, updatePos)
		self.updateCollidables()

	def pick(self):
		if len(self) == 1:
			self.HL.moveCenter(self.cards[0].rect.center)
		c = super().pick()
		self.drawables.remove(self.HL)
		self.updateCollidables()
		return c

	def empty(self):
		super().empty()
		self.collidables.empty()

	# donne un aperçu des cartes sélectionnées sans modifier la pile
	def peekSelection(self):
		pickedCards = []
		for c in self.cards:
			if c._layer > self.HL._layer:
				pickedCards.append(c)
		return pickedCards

	# crée une nouvelle pile avec les cartes au dessus du HL
	def pickSelected(self):
		pickedCards = self.peekSelection()
		if len(pickedCards) == 0:
			return None
		for c in pickedCards:
			self.cards.remove(c)
			self.drawables.remove(c)
		self.nextCardPos = pickedCards[0].rect.topleft
		self.updateCollidables()
		self.reposition(False)
		pickedCards[0].moveCenter(pg.mouse.get_pos())
		return CardPile2(self.type, pickedCards[0].rect.topleft, self.offset, pickedCards)

	# renvoie True si la souris est sur cette pile
	def update(self):
		super().update()
		L = pg.sprite.spritecollide(Point(pg.mouse.get_pos()), self.collidables, False)
		if len(L) > 0:
			L.sort(key = lambda s : s._layer)
			topCard = L[-1]
			self.HL.moveCenter(topCard.rect.center)
			self.drawables.add(self.HL)
			self.drawables.change_layer(self.HL, topCard._layer - 1)
			return True
		else:
			self.drawables.remove(self.HL)
			if len(self) == 0:
				return self.HL.rect.collidepoint(pg.mouse.get_pos())
			return False

	def drawHL(self, screen):
		self.HL.draw(screen)


class CardPile4(CardPile): # pile simple avec sélection et highlight
	def __init__(self, type, pos, cards=[]):
		super().__init__(type, pos, cards)
		self.HL = HighLightRect(white, cardW+2*space5, cardH+2*space5)
		self.HL.move((pos[0] - space5, pos[1] - space5))
		self.isMouseHere = False

	def pickSelected(self):
		card = self.pick()
		if card != None:
			return CardPile4(self.type, card.rect.topleft, [card])
		return None

	def followMouse(self):
		for c in self.cards:
			c.followMouse((0,0))

	def unfollowMouse(self):
		for c in self.cards:
			c.unfollowMouse()

	def update(self):
		if len(self) == 1:
			self.cards[0].update()
		self.isMouseHere = self.HL.rect.collidepoint(pg.mouse.get_pos())
		return self.isMouseHere

	def drawHL(self, screen):
		self.HL.draw(screen)

	def draw(self, screen):
		if len(self) > 0:
			if self.isMouseHere:
				self.drawHL(screen)
			self.cards[-1].draw(screen)