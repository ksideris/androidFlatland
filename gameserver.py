#!/usr/bin/env python

"""gameserver.py: Script to launch the game logic server."""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"

import pygame
import game.view as view
import game.environment as environment
from twisted.internet import reactor
import sys
import os

print os.curdir
pygame.init()
pygame.display.set_mode((800, 480), pygame.DOUBLEBUF)

tenv = environment.Environment()


a=view.Window(tenv)


print os.curdir
tenv.start()
reactor.run()


