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
import libs.beacon as beacon

try:
    import android
    import android.assets as assets
    print assets.list()
except ImportError:
    android = None
import sys, platform


print 'Looking for server'
while True:
    server = beacon.find_server(12000, b"flatland_arg")
    if server<>None:
        break
print 'Found server: ',server

pygame.init()
if platform.machine() == "armv7l":
    
    print 'GOING FULLSCREEN'
    displayFlags = pygame.DOUBLEBUF | pygame.FULLSCREEN
    pygame.mouse.set_visible(False)
    from game.actions_keyboard import PlayerController
    
    screen =pygame.display.set_mode((800, 480))
else:
    displayFlags = pygame.DOUBLEBUF
    screen =pygame.display.set_mode((800, 480), displayFlags)
    from game.actions_keyboard import PlayerController

'''
done=False	
while (not done):	
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True
        if  event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done=True
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 25)
 
    text = font.render("My text",True,[0,0,0])
    screen.blit(text, [250,250])
    pygame.display.flip()
'''    
#print 'Usage: gameclient.py player_id team'


#print("single: %r" % beacon.find_server(12000, b"abc"))

tenv = environment.Environment(2,2,server,'56000')

a=view.Window(tenv)
        
tenv.controller = PlayerController(a)
tenv.start()

