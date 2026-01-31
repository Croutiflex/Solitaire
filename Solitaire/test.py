from card import *
from properties import *
import random

def main():
	piles = [CardPileWithHL((0,0), unroll=(0, space2)) for i in range(7)]
	back = pg.image.load(cardsFolder + "back.png")
	allCards = [Card(i+1, back, cardSize) for i in range(52)]
	random.shuffle(allCards)
	deck = CardPile((space4, space3), cards=allCards)
	# for c in allCards:
	# 	deck.add(c)

	for i in range(10):
		card = deck.pick()
		x = i%7
		print("ajout carte ", card, " dans la pile ", x)
		piles[x].add(card)
		print("piles :")
		for p in piles:
			print(p)

if __name__ == '__main__':
	main()