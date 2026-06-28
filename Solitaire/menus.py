import pygame as pg
import json
from properties import *
from utils import *

fillRatio = 0.8

class StandardMenu():
	def __init__(self, configFile):
		file = open(menuConfigPath+configFile, 'r')
		menu = json.load(file)
		file.close()
		self.fileContent = menu
		self.drawables = pg.sprite.RenderPlain()

		# background
		bgconfig = menu["background"]
		w, h = W*menu["size"], H*menu["size"]
		bgcolor : pg.Color("black")
		match bgconfig["type"]:
			case "plain":
				bgcolor = randomColor(high=200) if bgconfig["value"] == "random" else pg.Color(bgconfig["value"]["r"], bgconfig["value"]["g"], bgconfig["value"]["b"])
				bg = ColorRect(bgcolor, w, h, pos=midScreen)
				self.drawables.add(bg)
			case "image":
				bg = BasicSprite(pg.transform.smoothscale(pg.image.load(menuResPath+bgconfig["value"]), (w,h)))
				bg.moveCenter(midScreen)
				self.drawables.add(bg)

		# title
		titleconfig = menu["title"]
		if titleconfig != "off":
			match titleconfig["type"]:
				case "text":
					font = pg.font.Font(font1, fontSize1)
					title = BasicSprite(font.render(titleconfig["value"], True, negativeColor(bgcolor), bgcolor))
					title.moveCenter((midx, bg.rect.top+h/10))
					self.drawables.add(title)

		# buttons
		tmp = menu["buttonlayout"].split("x")
		n, m = int(tmp[0]), int(tmp[1])
		x, y = bg.rect.left, bg.rect.top + h/5
		w2, h2 = w/(m+1), h*0.8/(n+1)
		buttonPos = [[(x+w2*(j+1), y+h2*(i+1)) for j in range(m)] for i in range(n)]
		self.buttons = []
		i, j = 0, 0
		for b in menu["buttons"]:
			button = Button(menuResPath+b["image1"], menuResPath+b["image2"], (scaleRatio*b["w"], scaleRatio*b["h"]), name=b["name"])
			button.moveCenter(buttonPos[i][j])
			self.buttons.append(button)
			self.drawables.add(button)
			j += 1
			if j == m:
				i += 1
				j = 0

	# renvoie le nom du bouton qui a été cliqué, None si aucun
	def click(self):
		for b in self.buttons:
			if b.isSelected:
				return b.name

	def update(self):
		self.drawables.update()

	def draw(self, screen):
		self.drawables.draw(screen)

class StandardMenu2():
	def __init__(self, configFile):
		file = open(menuConfigPath+configFile, 'r')
		config = json.load(file)
		file.close()
		self.drawables = pg.sprite.RenderUpdates()
		self.name = config["title"]
		w, h = W*menu["size"], H*menu["size"]
		self.size = w, h
		self.offset = config["contentOffset"]
		self.background = self.setBackground(config["background"])
		self.drawables.add(self.setBackground)
		self.setContent(config["content"])

	def setBackground(self, bgconfig):
		w, h = self.size
		v = bgconfig["value"]
		match bgconfig["type"]:
			case "plain":
				bgcolor = randomColor(high=200) if v == "random" else pg.Color(v["r"], v["g"], v["b"])
				return ColorRect(bgcolor, w, h, pos=midScreen)
			case "image":
				bg = BasicSprite(pg.transform.smoothscale(pg.image.load(menuResPath+v), (w,h)))
				bg.moveCenter(midScreen)
				return bg

	def setContent(self, content):
		self.buttons = []
		self.selectors = []
		w, h = self.size
		h -= self.offset
		currentPos = (self.background.rect.left, self.background.rect.top + self.offset)
		done = False
		context = content["content"]
		while not done:
			match content["obj"]:
				case "VBox":
					l = h/len(context)
					
					for elem in context:
						if context["obj"] == "HBox" or context["obj"] == "VBox":
							done = True
						else:
							self.parseElem(elem, )
				case "HBox":
					done = True

	def parseElem(self, elem, size, pos):
		match elem["obj"]:
			case "Selector1":
				selector = Selector1(elem["pathList"], size, pos=pos)
				self.selectors.append(selector)
				self.drawables.add(selector)
			case "Button":
				button = Button(menuResPath+elem["name"], size, pos=pos, name=elem["name"])
				self.buttons.append(button)
				self.drawables.add(button)

	# renvoie le nom du bouton qui a été cliqué, None si aucun
	def click(self):
		for b in self.buttons:
			if b.isSelected:
				return b.name
		for s in self.selectors:
			s.click()

	def update(self):
		self.drawables.update()

	def draw(self, screen):
		self.drawables.draw(screen)