import pygame as pg

# constantes
maxFramerate = 60
scaleRatio = 0.6
W = 1920*scaleRatio
H = 1080*scaleRatio
scaleRatio = W/1920
screenSize = (W, H)
midx = W/2
midy = H/2
midScreen = (midx, midy)
cardRatio = 192/128 # h/w
slideTime1 = 0.1
slideTime2 = 0.3
space1 = 20*scaleRatio
space2 = 50*scaleRatio
space3 = 75*scaleRatio
space4 = 150*scaleRatio
space5 = 5*scaleRatio
screenBottom = H - space1
backgroundColor = (100, 220, 100)
white = pg.Color(255, 255, 255, 255)

# texte
fontSize1 = int(50*scaleRatio)
font1 = 'freesansbold.ttf'

# dimensions
cardW = (W - 6*space3 - 2*space4)/7
cardH = cardW*cardRatio
cardSize = (cardW, cardH)

# couleurs
HEARTS = 0
CLUBS = 1
DIAMONDS = 2
SPADES = 3
colorLabel = ["Coeur","Trèfle","Carreau","Pique"]

# phases de jeu
DEAL = 0
GAME = 1
WIN = 2
END = 3

# path
menuConfigPath = "config/menu/"
cardsFolder = "res/cards/"
menuResPath = "res/menu/"
soundResPath = "res/sound/"