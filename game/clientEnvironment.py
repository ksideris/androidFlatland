

#!/usr/bin/env python

"""clientEnvironment.py: Environment contains all the higher level state of the game.
This is the client version. The relation between server-client is a master/slave
one. That is the client reads the current state and updates itself. It also
notifies the server of any client side events (actions /position updates)

"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"



import pygame
from vector import Vector2D
from game.player import Player,Building,ResourcePool

from game.network.asyncClient import AsyncClient
from libs.LoopingCall import LoopingThread


import time,random
import pickle,sys #TODO change to cPickle for speed

#import libs.shelve as shelve,
import os
#CLIENTLOCALDATA = 'ClientLocalData.db'

class Environment(LoopingThread): #in an MVC system , this would be a controller
    ''' The environment class contains the state of the game. The server has the master version, the clients have slave versions (updated through the network) '''
    ATTACK_RADIUS = 3
    SCAN_RADIUS = 3
    FPS=30
    

    def __init__(self,player_id,team,serverIP,serverPort):
                '''State: Players,Buildings, Time, Resourse Pool'''
                LoopingThread.__init__(self)               
		
		self.players 	= {}
		self.buildings 	= {}
		self.TimeLeft = 15*60 
		self.width = 80.0
		self.height = 48.0
		self.view =None
		self.GameOver =False
		self.playerID =player_id
		
		self.action = 0
		self.attemptedAction = 0
		self.lastAction = 0
		self.ActionTimeout = 1
		
		self.team =team
		self.otherTeam = 2 if self.team==1 else  1 
		self.scores =[0,0]
		self.IsServer = False
		self.ResourcePool = ResourcePool()
		self.client = AsyncClient(self)
		self.serverIP =serverIP
		self.serverPort = serverPort
                self.Tick = 0
                self.Position = (0,0)
                self.lastUpdate = 0
                self.controller = None


    def createPlayer(self, player_id,team):
                '''add a player to the given team'''
                player = Player()
                player.team = team

                playerId = id(player)
                player.player_id = player_id
               
                self.players[playerId] = player
        
                return player

    def createBuilding(self, team,pos):
                '''add a building to the given team'''
                building = Building()
                building.team = team
                building.position =pos
                bid = id(building)
                building.building_id = 0
                self.buildings[bid] = building
                
        
                return building
            
    def readGestures(self):
        self.controller._handleInput()

    def updateTime(self):
		self.Tick+= 1.0/Environment.FPS
		#if( self.TimeLeft<=0):
		#    self.GameOver =True
            
    def task(self):
                
		#self.deSerialize()
		self.readGestures()
		self.updateTime()
		self.updatePositions()
		self.makeRequest()
		self.view.paint(self.Tick )
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                self.shutdown()
                                pygame.quit()
                                sys.exit()
                        
		
    def makeRequest(self):
        #print self.action
        
        self.client.MakeRequest(self.playerID,self.team,self.action,self.Position)
        
        self.action = 0
    
    def updatePositions(self):
            for playerId in self.players:
                     
                     if self.players[playerId].player_id <> self.playerID:
                         
                         self.players[playerId].updatePosition( 1.0/Environment.FPS)
                     
    def start(self):
		'''controls the environment by initiating the looping calls'''

		self.lastUpdate =time.time()
		self.view.start('client-'+str(self.playerID))
		self.client.start(self.serverIP,self.serverPort)
		
                #if os.path.exists(CLIENTLOCALDATA.split('.')[0]+str(self.playerID)+'.'+CLIENTLOCALDATA.split('.')[1]):		
                #    os.remove(CLIENTLOCALDATA.split('.')[0]+str(self.playerID)+'.'+CLIENTLOCALDATA.split('.')[1])

		self.setInterval(1.0/Environment.FPS)
		self.run()
		#self._renderCall = LoopingCall(self.Update) 
		#self._requestCall = LoopingCall(self.makeRequest) 
		#self._renderCall.start(1.0/Environment.FPS)	
		#self._requestCall.start(1.0/Environment.FPS)	


	#FUNCTIONS FOR NETWORKING
	
    def deSerialize(self,state):
        
        try:
                
            '''
                assume the following message structure
                players$buildings$resourcepool$scores$timeleft$gameover

                    players->player1@player2@..@playern
                        player1->id&Team&sides&resources&partialResources&pos_x^pos_y&anim1^anim2^anim3&action
            '''
            if(state<>None):
                t = state.split('$')
                
                if(len(t)>0):
                    
                    players =  t[0].split('@') #update players
                    
                    players.remove('')
                    for p in players:
                          
                        found =False
                        pkey = 0
                        player = p.split('&')

                        pId     = int(player[0])
                        pTeam   = int (player[1])
                        pSides  = int(player[2])
                        pResources  = int(player[3])
                        pPartialResources = int(player[4])
                        pPosition = Vector2D( (float(player[5].split('^')[0]),(float(player[5].split('^')[1]))))
                        AnimationList = player[6].split('^')
                        AnimationList.remove('')
                        pAnimations=[]
                        for a in AnimationList:
                            a = a.split('#')
                            pAnimations.append( (int(a[0]),bool(a[1]),float(a[2])))
                        pAction = int(player[7])
                        
                        for ep in self.players.itervalues():
                            if ep.player_id == pId:
                                found = True
                                pkey = id(ep)
                                break
                        if found:
                            
                            self.players[pkey].sides = pSides
                            self.players[pkey].resources = pResources
                            self.players[pkey].partialResources = pPartialResources
                            
                            self.players[pkey].animations.extend(pAnimations)
                            
                            if pId == self.playerID:
                                
                                self.players[pkey].position = Vector2D(self.Position)
                                
                                self.players[pkey].action = self.action
                            else:
                                
                                self.players[pkey].targetPosition = pPosition
                                self.players[pkey].action = pAction
                        else:
                            
                            newplayer = self.createPlayer(pId,pTeam)
                            newplayer.targetPosition=pPosition
                            newplayer.sides = pSides
                            newplayer.resources = pResources
                            newplayer.partialResources = pPartialResources
                            newplayer.animations.extend(pAnimations)
                            newplayer.action = pAction

                    '''
                    assume the following message structure
                    players$buildings$resourcepool$scores$timeleft$gameover

                        buildings->buildings@buildings@..@buildings
                            buildings->id&Team&sides&resources&partialResources&pos_x^pos_y&anim1^anim2^anim3
                    '''
                 

                if(t[1]<>''):
                    
                    buildings  =  t[1].split('@')
                    
                    self.buildings.clear()
                    for b in buildings:
                        building = b.split('&')
                        bId = int(building[0])
                        bTeam = int(building[1])
                        bSides  = int(building[2])
                        bResources  = int(building[3])
                        bPartialResources = int(building[4])
                        AnimationList = building[6].split('^')
                        
                        AnimationList.remove('')
                        bAnimations=[]
                        for a in AnimationList:
                            a = a.split('#')
                            bAnimations.append( (int(a[0]),bool(a[1]),float(a[2])))
                            
                        bPosition = Vector2D( (float(building[5].split('^')[0]),(float(building[5].split('^')[1]))))

                        newbuilding = self.createBuilding(bTeam,bPosition)
                        newbuilding.building_id = bId
                        newbuilding.sides = bSides
                        newbuilding.resources = bResources
                        newbuilding.animations.extend(bAnimations)
                if(t[2]<>''):
                    self.scores =(int(t[2].split('^')[0]),int(t[2].split('^')[1]))
                if(t[3]<>''):
                    self.TimeLeft =int(t[3])
                if(t[4]<>''): 
                    self.GameOver = not bool(t[4])
                   
              
        except:
            print "Unexpected error:", sys.exc_info()[0]
