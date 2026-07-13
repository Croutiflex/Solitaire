import pygame as pg
import json
from properties import *
from utils import *

defaultSpacing = 25

class StandardMenu():
	def __init__(self, configFile):
		file = open(menuConfigPath+configFile, 'r')
		config = json.load(file)
		file.close()
		self.drawables = pg.sprite.RenderUpdates()
		self.name = config["title"]
		self.spacing = config["spacing"] if "spacing" in config else defaultSpacing
		[rw, rh] = config["size"] # ratios en 2D, par rapport à l'écran
		self.size = W*rw, H*rh
		self.offset = config["offset"] if "offset" in config else 0
		self.background = self.setBackground(config["background"])
		self.drawables.add(self.background)
		self.buttons = []
		self.selectors = []
		self.texts = {}
		self.setContent(config["content"])

	def setBackground(self, bgconfig):
		v = bgconfig["value"]
		match bgconfig["type"]:
			case "plain":
				bgcolor = randomColor(high=200) if v == "random" else pg.Color(v["r"], v["g"], v["b"])
				return ColorRect(bgcolor, self.size[0], self.size[1], pos=midScreen)
			case "image":
				bg = BasicSprite(pg.transform.smoothscale(pg.image.load(menuResPath+v), self.size))
				bg.moveCenter(midScreen)
				return bg

	def setContent(self, content, workArea=None): # recursive !
		if workArea == None: # premier appel
			w, h = self.size
			h -= self.offset
			workArea = pg.Rect(self.background.rect.left, self.background.rect.top + self.offset, w, h)
		else:
			(w, h) = workArea.size
		done = False
		context = content["content"]
		match content["obj"]:
			case "VBox":
				l = h/len(context)
				y = workArea.top
				for elem in context:
					if elem["obj"] == "HBox" or elem["obj"] == "VBox":
						self.setContent(elem, workArea=pg.Rect(workArea.left, y, workArea.w, l))
					else:
						self.parseElem(elem, pg.Rect(workArea.left+self.spacing, y+self.spacing, workArea.w-2*self.spacing, l-2*self.spacing))
					y += l
			case "HBox":
				l = w/len(context)
				x = workArea.left
				for elem in context:
					if elem["obj"] == "HBox" or elem["obj"] == "VBox":
						self.setContent(elem, workArea=pg.Rect(x, workArea.top, l, workArea.h))
					else:
						self.parseElem(elem, pg.Rect(x+self.spacing, workArea.top+self.spacing, l-2*self.spacing, workArea.h-2*self.spacing))
					x += l

	def parseElem(self, elem, rect):
		ofs = elem["offset"] if "offset" in elem else 0
		match elem["obj"]:
			case "Selector1":
				selector = Selector1(elem["options"], rect, offset=ofs, basePath=menuResPath, name=elem["name"], default=elem["default"])
				self.selectors.append(selector)
				self.drawables.add(selector)
			case "Button":
				button = Button(menuResPath+elem["path"], autoFillRect=rect, name=elem["name"])
				self.buttons.append(button)
				self.drawables.add(button)
			case "Carousel":
				carousel = Carousel(elem["options"], rect, offset=ofs, basePath=menuResPath, name=elem["name"], default=elem["default"])
				self.selectors.append(carousel)
				self.drawables.add(carousel)
			case "Text":
				txt = TextSprite(elem["value"], rect.size, pos=rect.center)
				self.texts[elem["name"]] = txt
				self.drawables.add(txt)

	# renvoie l'état des sélecteurs sous forme de dico
	def getSelected(self):
		ret = {}
		for s in self.selectors:
			ret[s.name] = s.selectedOpt
		return ret

	def setDefaultSelected(self, selection):
		for s in self.selectors:
			if s.name in selection:
				s.setSelectedOpt(selection[s.name])

	# change la valeur d'une balise texte du menu
	def setText(self, name, value):
		if name in self.texts:
			self.texts[name].setText(value)
		else:
			print("Erreur : la balise ", name, " n'existe pas dans le menu ", self.name)

	# renvoie le nom du bouton qui a été cliqué, None si aucun
	def click(self):
		for b in self.buttons:
			if b.isPressed:
				return b.name
		for s in self.selectors:
			s.click()

	def update(self):
		self.drawables.update()

	def draw(self, screen):
		self.drawables.draw(screen)