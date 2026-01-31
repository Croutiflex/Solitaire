import pygame as pg
import json
from properties import *
from utils import *

class StandardMenu():
	def __init__(self, configFile):
		file = open(menuConfigPath+configFile, 'r')
		menu = json.load(file)
		file.close()
		self.drawables = pg.sprite.RenderPlain()

		# background
		bgconfig = menu["background"]
		w, h = W*menu["size"], H*menu["size"]
		bgcolor : "black"
		match bgconfig["type"]:
			case "plain":
				bgcolor = randomColor(high=200) if bgconfig["value"] == "random" else pg.Color(bgconfig["value"]["r"], bgconfig["value"]["g"], bgconfig["value"]["b"])
				bg = HighLightRect(bgcolor, w, h, pos=midScreen)
				self.drawables.add(bg)

		# title
		titleconfig = menu["title"]
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
		w2, h2 = w/(n+1), h*0.8/(m+1)
		buttonPos = [[(x+w2*j, y+h2*i) for j in range(m)] for i in range(n)]
		self.buttons = []
		i, j = 0, 0
		for b in menu["buttons"]:
			button = Button(menuResPath+b["image1"], menuResPath+b["image2"], (b["w"], b["h"]))
			button.moveCenter(buttonPos[i][j])
			self.buttons.append(button)
			self.drawables.add(button)
			j += 1
			if j == m:
				i += 1
				j = 0

	def update(self):
		pass

	def draw(self, screen):
		self.drawables.draw(screen)