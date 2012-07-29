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

import libs.asyncore
import sys, platform

pygame.init()
if platform.machine() == "armv7l":
    
    print 'GOING FULLSCREEN'
    displayFlags = pygame.DOUBLEBUF | pygame.FULLSCREEN
    pygame.mouse.set_visible(False)
    from game.actions_keyboard import PlayerController
    
    print 'Step 1'
    pygame.display.set_mode((800, 480))
else:
    displayFlags = pygame.DOUBLEBUF
    pygame.display.set_mode((800, 480), displayFlags)
    from game.actions_keyboard import PlayerController
'''    
if (len(sys.argv) == 3):
        tenv = environment.Environment(int(sys.argv[1]),int(sys.argv[2]),\
                                       '127.0.0.1','80')
        a=view.Window(tenv)
        
        tenv.controller = PlayerController(a)
        tenv.start()
        
        #controller.go()
        #reactor.run()

else:
'''
#print 'Usage: gameclient.py player_id team'
print 'Step 2'
tenv = environment.Environment(0,1,'192.168.1.5','80')
print 'Step 3'
a=view.Window(tenv)
        
print 'Step 4'
tenv.controller = PlayerController(a)
tenv.start()

