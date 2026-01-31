import pygame as pg
from solitaire import *
from properties import *
from menus import *

def main():

	pg.init()
	pg.font.init()
	screen = pg.display.set_mode(screenSize, pg.SCALED | pg.FULLSCREEN)
	running = True
	clock = pg.time.Clock()

	mode = "menu"
	game = Solitaire()
	menu = StandardMenu("endmenu.json")

	while running:
		match mode:
			case "game":
				for event in pg.event.get():
					match event.type:
						case pg.QUIT: running = False
						case pg.MOUSEBUTTONDOWN:
							match event.button:
								case 1:
									if game.leftClick():
										mode = "menu"
								case 3:
									if game.rightClick():
										mode = "menu"
						case pg.MOUSEBUTTONUP:
							game.leftRelease()
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									mode = "menu"
								case pg.K_BACKSPACE:
									game = Solitaire()
								case pg.K_TAB:
									game.toggleCheat()
				game.update()
				game.draw(screen)
			case "menu":
				for event in pg.event.get():
					match event.type:
						case pg.KEYDOWN:
							match event.key:
								case pg.K_ESCAPE:
									running = False
				menu.update()
				menu.draw(screen)

		pg.display.flip()
		clock.tick(maxFramerate)

	pg.quit()

if __name__ == '__main__':
	main()