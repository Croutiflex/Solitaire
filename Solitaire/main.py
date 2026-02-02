import pygame as pg
from solitaire import *
from properties import *
from menus import *

def main():

	pg.init()
	pg.font.init()
	pg.mixer.init()
	screen = pg.display.set_mode(screenSize, pg.SCALED | pg.FULLSCREEN)
	screen = pg.display.set_mode(screenSize)
	running = True
	clock = pg.time.Clock()

	mode = "game"
	game = Solitaire()
	menuV = StandardMenu("victoryMenu.json")
	menuL = StandardMenu("defeatMenu.json")
	activeMenu = None

	while running:
		match mode:
			case "game":
				for event in pg.event.get():
					match event.type:
						case pg.QUIT: running = False
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									game.leftClick()
								case 3:
									game.rightClick()
							if game.phase == 2:
								mode = "menu"
								activeMenu = menuV if game.isWon else menuL
						case pg.MOUSEBUTTONUP:
							match event.button:
								case 1:
									game.leftRelease()
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									running = False
								case pg.K_BACKSPACE:
									game = Solitaire()
								case pg.K_TAB:
									game.toggleCheat()
				game.update()
				game.draw(screen)
			case "menu":
				for event in pg.event.get():
					match event.type:
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									match activeMenu.click():
										case "rejouer":
											game = Solitaire()
											mode = "game"
										case "quitter":
											running = False
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									running = False
				activeMenu.update()
				activeMenu.draw(screen)

		pg.display.flip()
		clock.tick(maxFramerate)

	pg.quit()

if __name__ == '__main__':
	main()