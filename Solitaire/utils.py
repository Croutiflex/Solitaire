import pygame as pg
import time
import random
from properties import *

def isOutOfScreen(pos):
	(x,y) = pos
	return x < 0 or y < 0 or x > W or y > H

def randomColor(low=0, high=255):
	return pg.Color(random.randint(low,high), random.randint(low,high), random.randint(low,high))

class BasicSprite(pg.sprite.Sprite):
	def __init__(self,image,layer=0,pos=(0,0)):
		pg.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect(x=pos[0], y=pos[1])
		self._layer = layer
	def moveCenter(self,pos):
		self.rect.center = pos
	def move(self,pos):
		self.rect.topleft = pos
		if isOutOfScreen(pos):
			print("Sprite hors de l'écran! ", pos)
	def draw(self,screen):
		screen.blit(self.image, self.rect)
	# renvoie une copie simplifliée de n'importe quel sprite
	def basicCopy(self, pos):
		return BasicSprite(self.image, layer=self._layer, pos=self.rect.topleft)

class HighLightRect(BasicSprite):
	def __init__(self,color,width,height,layer=-1,pos=(0,0)):
		super().__init__(pg.Surface([width, height]), layer)
		self.image.fill(color)
		self.moveCenter(pos)
	def set_color(self,color):
		self.image.fill(color)

# a sprite that can be animated to move in a straight line to a given destination
class SpriteWithTL(BasicSprite):
	def __init__(self,image,layer=0,pos=(0,0)):
		super().__init__(image,layer,pos)
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
	def __init__(self, path1, path2, size, pos=(0,0)):
		pg.sprite.Sprite.__init__(self)
		self.imgOn = pg.transform.smoothscale(pg.image.load(path2), size)
		self.imgOff = pg.transform.smoothscale(pg.image.load(path1), size)
		self.isSelected = False
		super().__init__(self.imgOff, pos=pos)
	def update(self):
		if self.rect.collidepoint(pg.mouse.get_pos()):
			self.image = self.imgOn
			self.isSelected = True
		else:
			self.image = self.imgOff
			self.isSelected = False

class CloseButton(Button):
	def __init__(self):
		h2 = screenSize[1]/20
		size = (h2, h2)
		Button.__init__(self, "res/X.png", "res/X2.png", size, (screenSize[0] - h2*2, h2))