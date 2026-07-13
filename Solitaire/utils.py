import pygame as pg
import time
import random
import os
from properties import *

def isOutOfScreen(pos):
	(x,y) = pos
	return x < 0 or y < 0 or x > W or y > H

def randomColor(low=0, high=255):
	return pg.Color(random.randint(low,high), random.randint(low,high), random.randint(low,high))

# renvoie la couleur opposée à la couleur donnée
def negativeColor(c : pg.Color):
	return pg.Color(255-c.r, 255-c.g, 255-c.b)

def playRandomSound(soundList):
	soundList[random.randint(0,len(soundList)-1)].play()

class BasicSprite(pg.sprite.Sprite):
	def __init__(self,image,size=None,layer=0,pos=(0,0)):
		pg.sprite.Sprite.__init__(self)
		self.image = image if size == None else pg.transform.smoothscale(image, size)
		self.rect = self.image.get_rect(x=pos[0], y=pos[1])
		self._layer = layer
	def moveCenter(self,pos):
		self.rect.center = pos
	def move(self,pos):
		self.rect.topleft = pos
		if isOutOfScreen(pos):
			print("Sprite hors de l'écran! ", pos)
	def setImage(self, image):
		self.image = pg.transform.smoothscale(image, self.rect.size)
	def draw(self,s):
		s.blit(self.image, self.rect)
	# renvoie une copie simplifliée de n'importe quel sprite
	def basicCopy(self, pos):
		return BasicSprite(self.image, layer=self._layer, pos=self.rect.topleft)

class ColorRect(BasicSprite):
	def __init__(self,color,width,height,layer=-1,pos=(0,0)):
		super().__init__(pg.Surface([width, height]), layer=layer)
		self.image.fill(color)
		self.moveCenter(pos)
	def set_color(self,color):
		self.image.fill(color)

class TextSprite(BasicSprite):
	def __init__(self,text,size,backgroundColor=None,textColor="black",pos=(0,0)):
		self.font = pg.font.Font('freesansbold.ttf', max(int(size[1]), 25))
		self.backgroundColor = backgroundColor
		self.textColor = textColor
		super().__init__(pg.Surface(size))
		self.moveCenter(pos)
		self.setText(text)
	def setText(self, text):
		self.image = self.font.render(text, True, self.textColor, self.backgroundColor)
		self.rect = self.image.get_rect(center=self.rect.center)

# a sprite that can be animated to move in a straight line to a given position
class SpriteWithTL(BasicSprite):
	def __init__(self,image,layer=0,size=None,pos=(0,0)):
		super().__init__(image,layer=layer,size=size,pos=pos)
		self.done = True

	# tell the sprite to start moving to dest = (x,y)
	# the sprite will also shrink or grow depending on the resize value (1 = no resizing)
	# when dest is reached, execute function onDone.
	def animate(self, dest, onDone=None, resize=1, duration=slideTime1):
		start = self.rect.topleft
		self.speedVector = ((dest[0]-start[0])/duration, (dest[1]-start[1])/duration)
		if resize != 1:
			self.resizing = True
			self.resizeSpeed = (resize-1)/duration
			self.currentInflation = 1
			self.baseImg = self.image
		else:
			self.resizing = False
		self.duration = duration
		self.lastFrameTime = None
		self.elapsedTime = 0
		self.done = False
		self.onDone = onDone
	def resetAnimation(self):
		self.lastFrameTime = None
		self.speedVector = (0,0)
		self.elapsedTime = 0
		self.done = True
		self.onDone = None
	def update(self):
		if not self.done:
			# print('elapsedTime: ', self.elapsedTime)
			if self.lastFrameTime == None: # premiere frame du mouvement
				self.lastFrameTime = time.time()
				return
			now = time.time()
			dt = now - self.lastFrameTime
			self.lastFrameTime = now
			self.elapsedTime += dt
			if self.resizing:
				self.currentInflation += self.resizeSpeed*dt
				self.image = pg.transform.smoothscale_by(self.baseImg, self.currentInflation)
				pos = self.rect.topleft
				self.rect.scale_by_ip(self.currentInflation)
				self.rect.topleft = pos
			dx, dy = self.speedVector[0]*dt, self.speedVector[1]*dt
			self.rect.topleft = (self.rect.left + dx, self.rect.top + dy)
			if self.elapsedTime >= self.duration:
				if self.onDone != None:
					self.onDone()
				self.resetAnimation()

class Point(pg.sprite.Sprite):
	def __init__(self, pos):
		(x, y) = pos
		pg.sprite.Sprite.__init__(self)
		self.rect = pg.Rect(x, y, 1, 1)

# bouton avec 2 images (survolé ou pas)
class Button(BasicSprite):
	def __init__(self, path, size=None, pos=(0,0), name="button", autoFillRect=None):
		if not autoFillRect and not size:
			print("Erreur création Button : spécifier size ou autoFillRect")
			return None
		# autoFillRect : remplir un espace en préservant les proportions de l'image.
		if not os.path.isfile(path):
			path = dummyImg
		if autoFillRect != None:
			img1 = pg.image.load(path)
			r = img1.get_rect()
			if r.w/r.h > autoFillRect.w/autoFillRect.h: # image + large que l'espace donné
				size = (autoFillRect.w, autoFillRect.w*r.h/r.w)
			else:
				size = (autoFillRect.h*r.w/r.h, autoFillRect.h)
		self.imgOff = pg.transform.smoothscale(pg.image.load(path), size)
		self.imgOn = pg.transform.smoothscale(pg.image.load(getPushedButtonPath(path)), size)
		self.name = name
		self.isPressed = False
		super().__init__(self.imgOff, pos=pos)
		if autoFillRect != None:
			self.moveCenter(autoFillRect.center)
	def update(self, mouseOffSet=(0,0)):
		mp = pg.mouse.get_pos()
		if self.rect.collidepoint((mp[0]+mouseOffSet[0], mp[1]+mouseOffSet[1])):
			self.image = self.imgOn
			self.isPressed = True
		else:
			self.image = self.imgOff
			self.isPressed = False

class CloseButton(Button):
	def __init__(self):
		h2 = screenSize[1]/20
		size = (h2, h2)
		super().__init__(self, "res/X.png", size=size, pos=(screenSize[0] - h2*2, h2))

# bouton amélioré permettant de choisir entre plusieurs options
# optList = liste des options, chacune doit avoir une image du même nom dans basePath.
class Selector1(BasicSprite):
	def __init__(self, optList, rect, offset=0, basePath="", name="selector", default=0):
		self.name = name
		size = rect.size
		super().__init__(pg.Surface(size), size=size, pos=rect.topleft)
		optSize = ((size[0]-(len(optList)-1)*space5)/len(optList), (size[1]-offset)/2)
		self.options = [Button(basePath+optList[i]["path"], size=optSize, pos=(i*(optSize[0]+space5), offset)) for i in range(len(optList))]
		self.values = [opt["value"] for opt in optList]
		indicatorSize = (optSize[0]-2*space5, optSize[1]-space5)
		self.indicatorPos = [(self.options[i].rect.left+space5, optSize[1]+offset+space5) for i in range(len(optList))]
		self.indicator = BasicSprite(pg.image.load(basePath+"applique.png"), size=indicatorSize, pos=self.indicatorPos[default])
		self.background = BasicSprite(pg.image.load(basePath+name+".png"), size=size)
		self.drawables = pg.sprite.RenderUpdates([self.background] + self.options + [self.indicator])
		self.selectedOpt = self.values[default]
	def setSelectedOpt(self, opt):
		i = 0
		for v in self.values:
			if opt == v:
				self.selectedOpt = opt
				self.indicator.move(self.indicatorPos[i])
			i += 1
	def click(self):
		i = 0
		for opt in self.options:
			if opt.isPressed:
				self.selectedOpt = self.values[i]
				self.indicator.move(self.indicatorPos[i])
				self.selectedOpt
			i += 1
	def update(self):
		self.drawables.update(mouseOffSet=(-self.rect.left,-self.rect.top))
		self.image.fill("black")
		self.drawables.draw(self.image)
	def draw(self, screen):
		super().draw(screen)

class Carousel(BasicSprite):
	def __init__(self, optList, rect, offset=0, basePath="",name="carousel", default=1):
		if len(optList) < 3:
			print("Erreur : un carousel doit avoir au moins 3 options")
			return
		self.name = name
		# fit size while keeping proportions
		sizeRatio = 500/(100+offset) # w/h
		(w,h) = rect.size
		if w/h > sizeRatio:
			c = rect.center
			rect.w = sizeRatio*h
			rect.center = c
		else:
			c = rect.center
			rect.h = w/sizeRatio
			rect.center = c
		super().__init__(pg.Surface(rect.size), size=rect.size, pos=rect.topleft)
		self.background = BasicSprite(pg.image.load(basePath+name+".png"), size=rect.size)
		img = pg.image.load(basePath+optList[0]+".png")
		img2 = pg.transform.scale_by(img, (self.rect.h-offset)/img.get_rect().h)
		self.largeOptSize = img2.get_rect().size
		self.smallOptSize = (self.largeOptSize[0]/2, self.largeOptSize[1]/2)
		# Options affichées
		self.options = optList
		self.optionsImg = [pg.image.load(basePath+opt+".png") for opt in optList]
		self.selectedOptIndex = default
		self.selectedOpt = self.options[default]
		cy = (self.rect.h-offset)/2+offset
		dx = self.rect.h-offset
		self.centerOpt = BasicSprite(self.optionsImg[getIndexInRange(len(self.options), default)], size=self.largeOptSize)
		self.centerOpt.moveCenter((self.rect.w/2, cy))
		self.leftOpt = BasicSprite(self.optionsImg[getIndexInRange(len(self.options), default-1)], size=self.smallOptSize)
		self.leftOpt.moveCenter((self.rect.w/2 - dx, cy))
		self.rightOpt = BasicSprite(self.optionsImg[getIndexInRange(len(self.options), default+1)], size=self.smallOptSize)
		self.rightOpt.moveCenter((self.rect.w/2 + dx, cy))
		self.drawables = pg.sprite.RenderUpdates([self.background, self.rightOpt, self.leftOpt, self.centerOpt])
		# boutons flèches
		bh = self.rect.h/2
		self.leftBt = Button(basePath+"left.png", (bh,bh), name="left")
		self.leftBt.rect.centery = cy
		self.leftBt.rect.left = 0
		self.rightBt = Button(basePath+"right.png", (bh,bh), name="right")
		self.rightBt.rect.centery = cy
		self.rightBt.rect.right = self.rect.w
		self.drawables.add([self.rightBt, self.leftBt])
	def incrementIndex(self, inc):
		self.selectedOptIndex = getIndexInRange(len(self.options), self.selectedOptIndex+inc)
	def updateOpt(self):
		self.leftOpt.setImage(self.optionsImg[getIndexInRange(len(self.options), self.selectedOptIndex-1)])
		self.centerOpt.setImage(self.optionsImg[self.selectedOptIndex])
		self.rightOpt.setImage(self.optionsImg[getIndexInRange(len(self.options), self.selectedOptIndex+1)])
		self.selectedOpt = self.options[self.selectedOptIndex]
	def setSelectedOpt(self, optName):
		for i in range(len(self.options)):
			if self.options[i] == optName:
				self.selectedOptIndex = i
				self.updateOpt()
	def click(self):
		if self.leftBt.isPressed:
			self.incrementIndex(-1)
			self.updateOpt()
		elif self.rightBt.isPressed:
			self.incrementIndex(1)
			self.updateOpt()
	def update(self):
		self.drawables.update(mouseOffSet=(-self.rect.left,-self.rect.top))
		self.drawables.draw(self.image)
	def draw(self, screen):
		super().draw(screen)

# in : "button.png"
# out : "button2.png"
def getPushedButtonPath(path):
	l = path.split(".")
	ret = l[0]+"2."+l[1]
	if os.path.isfile(ret):
		return ret
	else:
		return dummyImg

def getIndexInRange(listLen, index):
	if index < 0:
		return listLen + index
	elif index >= listLen:
		return index - listLen
	return index