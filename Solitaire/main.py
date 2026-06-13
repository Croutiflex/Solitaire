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
	# menuV = StandardMenu("victoryMenu.json")
	# menuL = StandardMenu("defeatMenu.json")
	# pauseMenu = StandardMenu("pauseMenu.json")
	activeMenu = None

	# test __________________________
	mode = "test"
	selector = Selector1([menuResPath+"options.png", menuResPath+"reprendre.png", menuResPath+"newgame.png"], (600, 100), pos=(100,100))
	# _______________________________

	while running:
		match mode:
			case "game":
				game.update()
				game.draw(screen)
				for event in pg.event.get():
					match event.type:
						case pg.QUIT: running = False
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									game.leftClick()
								case 3:
									game.rightClick()
						case pg.MOUSEBUTTONUP:
							match event.button:
								case 1:
									game.leftRelease()
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									mode = "menuPause"
								case pg.K_BACKSPACE:
									game = Solitaire()
								case pg.K_TAB:
									game.toggleCheat()
				if game.phase == END:
					mode = "menuEnd"
					activeMenu = menuV if game.isWon else menuL
				elif game.phase == CASCADE:
					mode = "cascade"
			case "menuPause":
				pauseMenu.update()
				pauseMenu.draw(screen)
				for event in pg.event.get():
					match event.type:
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									match pauseMenu.click():
										case "newgame":
											game = Solitaire()
											mode = "game"
										case "options":
											pass
										case "retour":
											mode = "game"
										case "quitter":
											running = False
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									mode = "game"
			case "menuEnd":
				activeMenu.update()
				activeMenu.draw(screen)
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
									pass
			case "cascade":
				game.update()
				game.draw(screen)
				for event in pg.event.get():
					match event.type:
						case pg.QUIT: running = False
						case pg.KEYDOWN:
							mode = "menuEnd"
							activeMenu = menuV
							game.cleanup()
				if game.phase == END:
					mode = "menuEnd"
					activeMenu = menuV
			case "test":
				selector.update()
				selector.draw(screen)
				for event in pg.event.get():
					match event.type:
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									selector.click()
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									running = False

		pg.display.flip()
		clock.tick(maxFramerate)

	pg.quit()

if __name__ == '__main__':
	main()