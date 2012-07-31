#!/usr/bin/env python

"""gameclient.py: Script to launch a game client.
    Need to be invoked as follows:
    python gameclient.py player_id team
    TODO: make the server location more configurable
"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"

import pygame
import game.view as view
import game.clientEnvironment as environment

import sys, platform

pygame.init()
if platform.machine() == "armv7l":
    
    print 'GOING FULLSCREEN'
    displayFlags = pygame.DOUBLEBUF | pygame.FULLSCREEN
    pygame.mouse.set_visible(False)
    from game.actions_keyboard import PlayerController
    
    pygame.display.set_mode((800, 480))
else:
    displayFlags = pygame.DOUBLEBUF
    pygame.display.set_mode((800, 480), displayFlags)
    from game.actions_keyboard import PlayerController


#print 'Usage: gameclient.py player_id team'

tenv = environment.Environment(0,1,'127.0.0.1','80')

a=view.Window(tenv)
        
tenv.controller = PlayerController(a)
tenv.start()

