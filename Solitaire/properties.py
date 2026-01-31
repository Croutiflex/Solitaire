import pygame as pg

# constantes
maxFramerate = 60
W = 1920
H = 1080
screenSize = (W, H)
cardRatio = 192/128 # h/w
slideTime1 = 0.1
slideTime2 = 0.3
space1 = 20
space2 = 50
space3 = 75
space4 = 150
space5 = 5
screenBottom = H - space1
backgroundColor = (100, 220, 100)
white = pg.Color(255, 255, 255, 255)

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
END = 2

# path
menuResPath = "config/menu/"
cardsFolder = "res/cards/"