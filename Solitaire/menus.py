import pygame as pg
import json
from properties import *

class StandardMenu():
	def __init__(self, configFile):
		menu = json.load(open(menuResPath+configFile, 'r'))
		