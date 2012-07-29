

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
#from game.network.SimpleClient import SimpleClient
from game.network.asyncClient import AsyncClient
from libs.LoopingCall import LoopingThread


import time,random
import pickle,sys #TODO change to cPickle for speed

#import libs.shelve as shelve,
import os
CLIENTLOCALDATA = 'ClientLocalData.db'

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
		self.ResourcePool = None
		self.client = AsyncClient(self)
		self.serverIP =serverIP
		self.serverPort = serverPort
                self.Tick = 0
                self.Position = (0,0)
                self.lastUpdate = 0
                self.controller = None
                
    def readGestures(self):
        self.controller._handleInput()

    def updateTime(self):
		self.Tick+= 1.0/Environment.FPS
		#if( self.TimeLeft<=0):
		#    self.GameOver =True
            
    def task(self):
                
		#self.deSerialize()
		self.updateTime()
		self.updatePositions()
		self.readGestures()
		self.view.paint(self.Tick )
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                self.shutdown()
                                pygame.quit()
                                sys.exit()
                        
		
    def makeRequest(self,action,Position):
        #print self.action
        
        self.client.MakeRequest(self.playerID,self.team,action,Position)
        
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
		
                if os.path.exists(CLIENTLOCALDATA.split('.')[0]+str(self.playerID)+'.'+CLIENTLOCALDATA.split('.')[1]):		
                    os.remove(CLIENTLOCALDATA.split('.')[0]+str(self.playerID)+'.'+CLIENTLOCALDATA.split('.')[1])

		self.setInterval(1.0/Environment.FPS)
		self.run()
		#self._renderCall = LoopingCall(self.Update) 
		#self._requestCall = LoopingCall(self.makeRequest) 
		#self._renderCall.start(1.0/Environment.FPS)	
		#self._requestCall.start(1.0/Environment.FPS)	


	#FUNCTIONS FOR NETWORKING
	
    def deSerialize(self,state):
        #state=None
        #localdb = shelve.open(CLIENTLOCALDATA.split('.')[0]+str(self.playerID)+'.'+CLIENTLOCALDATA.split('.')[1])
        try:#:#localdb.has_key('data'):
                
            '''try:

                state = localdb['data']['string']             

            finally:
                localdb.close()
            '''       
            if(state<>None):
                t = state.split('$')
                print t[0]
                print t[1]
                print t[2]
                players =  pickle.loads(t[0]) #update players
                #self.players.clear()
                
		print 'step 1'
                for p in players.itervalues():
                    found =False
                    pkey = 0
                    for ep in self.players.itervalues():
                        if ep.player_id == p.player_id :
                            found=True
                            pkey = id(ep)
                            break
                    if found:         
                        self.players[pkey].sides = p.sides
                        self.players[pkey].resources = p.resources
                        self.players[pkey].partialResources = p.partialResources
                        self.players[pkey].animations.extend(p.animations)
                        
                        if p.player_id == self.playerID:
                                    self.players[pkey].position = Vector2D(self.Position)
                                    self.players[pkey].action = self.action
                        else:
                            self.players[pkey].targetPosition = p.position
                            self.players[pkey].action = p.action
                    else:
                        self.players[id(p)]=p
                buildings =  pickle.loads(t[1]) #update buildings
		print 'step 2'
                self.buildings.clear()
                for b in buildings.itervalues():                    
                    self.buildings[id(b)] = b
		print t[2]
				
                self.ResourcePool = pickle.loads(t[2])
		print 'step 3'
		print t[3]
                self.scores =pickle.loads(t[3])
		print 'step 4'
                self.TimeLeft =int(t[4])
		print 'step 5'
                
               
                self.GameOver = not bool(t[6]) #weird
              
		print 'step 6'
        except:
            print "Unexpected error:", sys.exc_info()[0]
