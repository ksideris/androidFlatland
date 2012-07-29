"""
actions_wand handles input from phones, in particular interprets accelerometer data
for gesture recognition.  The heavy lifting for gesture recognition happens in function
getAccelReading()
"""

from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import math

import pygame.event
import pygame.mouse
import pygame.time
import sys

#Added these imports for gesture recognition
import accelreader
import pickle
from copy import deepcopy

ACCEL_READ_WINDOW_LENGTH = 30

# TODO: Can we have a keymap file?
from pygame import (K_a as ATTACK,
                    K_s as SCAN,
                    K_d as BUILD,
                    K_w as UPGRADE,
                    K_ESCAPE as QUIT,
                    K_DOWN as MOVE_DOWN,
                    K_UP as MOVE_UP,
                    K_LEFT as MOVE_LEFT,
                    K_RIGHT as MOVE_RIGHT,
                    K_z as SWITCH_TEAMS)

from game.vector import Vector2D

class PlayerController(object):
    """
    Input handler for L{game.player.Player} objects.

    @ivar player: The player being controlled.
    @ivar downDirections: List of currently held arrow keys.
    """
    BUTTON = 3
    JITTER_COUNT = 3
    JITTER_VOTES = 2

    def __init__(self, perspective, view):
        self.perspective = perspective
        self.position = Vector2D(0, 0)
        self.speed = 10
        self.view = view
        self._actionQueue = []
        self._currentAction = None
        self._lastAction = None

        #Added these for gesture recognition
        # These are for a more sophisticated gesture recognition technique, that was hastily abandoned.
        self._scan = self._loadPattern("game/pickles/scanRightPattern.pickle")
        self._upgrade = self._loadPattern("game/pickles/scanLeftPattern.pickle")
        self._attack = self._loadPattern("game/pickles/attackPattern.pickle")
        self._build = self._loadPattern("game/pickles/buildPattern.pickle")
        self._areas = self._loadPattern("game/pickles/areas.pickle")
        #this is a list of area transitions
        self._sampleData = self._initPattern(1)
        self._transitionAverages = self._initPattern(1)
        #this is the current serial data
        self._serialData = {}
        self._serialData[self.BUTTON] = 0
        self._currentPattern = None
        self._sampleCnt = 0
        self._lastPosition = (0,0,0)
        self._ser = accelreader.AccelReader()

        self.accelerometerPollFunc = None

        self._movingUp = False
        self._movingDown = False
        self._movingLeft = False
        self._movingRight = False



    def go(self):
        #print("Listen!")
        #self.startGestureListen()
        self.previousTime = pygame.time.get_ticks()
        self._inputCall = LoopingCall(self._handleInput)
        d = self._inputCall.start(0.03)
        return d


    def stop(self):
        self._inputCall.stop()


    def _updatePosition(self, dt):
        if not pygame.mouse.get_focused() or not dt:
            return
        destination = self.view.worldCoord(Vector2D(pygame.mouse.get_pos()))
        direction = destination - self.position
        if direction < (self.speed * dt):
            #self.position = destination
            pass
        else:
            #self.position += (dt * self.speed) * direction.norm()
            pass

        #if direction < (self.speed * dt):
        #    self.position = destination
        #else:
        #    self.position += (dt * self.speed) * direction.norm()

        #=======================================================================
        directionX = 0
        directionY = 0

        if (self._movingUp):
            directionY = -1
        elif self._movingDown:
            directionY = 1

        if (self._movingLeft):
            directionX = -1
        elif self._movingRight:
            directionX = 1

        direction = Vector2D(directionX, directionY)#destination - self.position

        
        
        #if directionX != 0 or directionY != 0:
        #    self.position += (dt * self.speed) * direction.norm()
        #=======================================================================
	#This fixed mining. But why was it disabled? What else is commented out?
        self.perspective.callRemote('updatePosition',Vector2D(-1000, -1000))
        #self.view.setCenter(self.position)


    def _startedAction(self, action):
        actionBeforeLast = self._lastAction
        self._lastAction = self._currentAction
        self._currentAction = action
        if self._currentAction == ATTACK:
            if self._lastAction != ATTACK:
                self.perspective.callRemote('startAttacking')
        elif self._currentAction == BUILD:
            if self._lastAction != BUILD:
                self.perspective.callRemote('startBuilding')
        elif self._currentAction == SCAN:
            if self._lastAction != SCAN:
                self.perspective.callRemote('startScanning')
                self.view.addAction("sweep")
        elif self._currentAction == UPGRADE:
            if self._lastAction != UPGRADE:
                self.perspective.callRemote('startUpgrading')
        else:
            if self._lastAction == None:
                self._currentAction = None


    def _finishedAction(self):
        if self._currentAction == ATTACK:
            self.perspective.callRemote('finishAttacking')
        elif self._currentAction == BUILD:
            self.perspective.callRemote('finishBuilding')
        elif self._currentAction == SCAN:
            self.perspective.callRemote('finishScanning')
        elif self._currentAction == UPGRADE:
            self.perspective.callRemote('finishUpgrading')
        self._currentAction = None
        return





    '''
    This is the function that actually interprets the accelerometer data.
    
    It currently does something a little dumb and only examines data over
    non-overlapping windows of time where as it should use more of sliding
    window scheme, which would probably have lower latency.
    '''
    def getAccelReading(self):

        self.nReadings = (self.nReadings + 1) % ACCEL_READ_WINDOW_LENGTH
        data = self._readSerial()#reader.get_pos()

        newToOldRatio = .2

        for i in range(0,3):
            #dynamicAvg[i] = dynamicAvg[i] + (data[i] - lastOne[i])*(data[i] - lastOne[i])
            #avg[i] = avg[i] + data[i]*data[i]*getSignMultiplier(data[i])

            self.dynamicAvg[i] = (1 - newToOldRatio)*self.dynamicAvg[i] + newToOldRatio*(data[i] - self.lastOne[i])*(data[i] - self.lastOne[i])
            self.avg[i]        = (1 - newToOldRatio)*self.avg[i] + newToOldRatio*data[i]*data[i]*self.getSignMultiplier(data[i])

            self.lastOne[i] = data[i]


        if self.nReadings == 0:
        #=======================================================================
            movingTooMuchForUpgrade = False
            movingSlowEnoughForUpgrade = True

            signlessAvg = self.avg
            for i in range(0,3):
                #dynamicAvg[i] = dynamicAvg[i] #/ nCycles
                #avg[i] = avg[i] #/ nCycles
                signlessAvg[i] = abs(self.dynamicAvg[i])
                movingTooMuchForUpgrade = movingTooMuchForUpgrade or signlessAvg[i] > 10000
                movingSlowEnoughForUpgrade = movingSlowEnoughForUpgrade and signlessAvg[i] < 7


            stormiestDimension = self.dynamicAvg.index(max(self.dynamicAvg))

                #check for the upgrading gesture (static)
            if self.lastOne.index(max(self.lastOne)) == 0 and self.lastOne[0] > 800:# and not movingTooMuchForUpgrade and movingSlowEnoughForUpgrade:
                print("upgrade")
                self._startedAction(UPGRADE)
                    #
         #self._startedAction(UPGRADE)
    #            #check for dynamic gestures

            elif movingTooMuchForUpgrade:
    #                if signlessAvg.index(max(signlessAvg)) == 0 and avg[0] > 0 and stormiestDimension == 2:
    #                    print("upgrade")
    #                el
                if stormiestDimension == 0:
                    print("attack")
                    self._startedAction(ATTACK)
                    #self._startedAction(ATTACK)
                elif stormiestDimension == 1:
                    print("scan")
                    self._startedAction(SCAN)

                    #self._startedAction(SCAN)
                elif stormiestDimension == 2:
                    print("build")
                    self._startedAction(BUILD)
                    #self._startedAction(BUILD)
            else:
                print("none")
                self._finishedAction()

            # ===== print totals ======
            print "prev:\nX: " + str(self.lastOne[0]) +"\nY: " +  str(self.lastOne[1]) + "\nZ: " + str(self.lastOne[2]) + "\n"
            print "\nacc:\nX: " + str(self.avg[0]) +"\nY: " +  str(self.avg[1]) + "\nZ: " + str(self.avg[2]) + "\n"
            print "\njerk:\nX: " + str(self.dynamicAvg[0]) +"\nY: " +  str(self.dynamicAvg[1]) + "\nZ: " + str(self.dynamicAvg[2]) + "\n\n"

            self.dynamicAvg = [0, 0, 0]
            self.avg = [0, 0, 0]
            self.lastOne = [0, 0, 0]

        #=======================================================================
        #=======================================================================



    def pollAccelerometer(self):
        dynamicAvg = [0, 0, 0]
        avg = [0, 0, 0]
        lastOne = [0, 0, 0]
        nChecks = 0
        nCycles = 75

        for i in range(0, nCycles):
            data = self._readSerial()#reader.get_pos()

            newToOldRatio = .2

            for i in range(0,3):
                #dynamicAvg[i] = dynamicAvg[i] + (data[i] - lastOne[i])*(data[i] - lastOne[i])
                #avg[i] = avg[i] + data[i]*data[i]*getSignMultiplier(data[i])

                dynamicAvg[i] = (1 - newToOldRatio)*dynamicAvg[i] + newToOldRatio*(data[i] - lastOne[i])*(data[i] - lastOne[i])
                avg[i]        = (1 - newToOldRatio)*avg[i] + newToOldRatio*data[i]*data[i]*self.getSignMultiplier(data[i])

                lastOne[i] = data[i]

            nChecks = (nChecks + 1) % nCycles
            pygame.time.wait(10)


        #=======================================================================

        movingTooMuchForUpgrade = True

        signlessAvg = avg
        for i in range(0,3):
            #dynamicAvg[i] = dynamicAvg[i] #/ nCycles
            #avg[i] = avg[i] #/ nCycles
            signlessAvg[i] = abs(avg[i])
            movingTooMuchForUpgrade = movingTooMuchForUpgrade and dynamicAvg[i] > 7


        stormiestDimension = dynamicAvg.index(max(dynamicAvg))

        if self._currentAction == None:
            pass
            #check for the upgrading gesture (static)
        if lastOne.index(max(lastOne)) == 0 and lastOne[0] > 900 and not movingTooMuchForUpgrade:# and movingSlowEnoughForUpgrade:
            print("upgrade")
            self._startedAction(UPGRADE)
                #
     #self._startedAction(UPGRADE)
#            #check for dynamic gestures

        elif movingTooMuchForUpgrade:
#                if signlessAvg.index(max(signlessAvg)) == 0 and avg[0] > 0 and stormiestDimension == 2:
#                    print("upgrade")
#                el
            if stormiestDimension == 0:
                print("attack")
                self._startedAction(ATTACK)
                #self._startedAction(ATTACK)
            elif stormiestDimension == 1:
                print("scan")
                self._startedAction(SCAN)

                #self._startedAction(SCAN)
            elif stormiestDimension == 2:
                print("build")
                self._startedAction(BUILD)

        # ===== print totals ======
        #print "\njerk:\nX: " + str(dynamicAvg[0]) +"\nY: " +  str(dynamicAvg[1]) + "\nZ: " + str(dynamicAvg[2])


        #print "\nacc:\nX: " + str(avg[0]) +"\nY: " +  str(avg[1]) + "\nZ: " + str(avg[2]) + "\n\n"
        #=======================================================================



    def getSignMultiplier(self,num):
        if num < 0:
            return -1
        else:
            return 1

    def startGestureListen(self):
        #self.accelerometerPollFunc = LoopingCall(self.pollAccelerometer)
        #self.accelerometerPollFunc.start(.3, now=True)
        self.pollAccelerometer()
        #don't start immediately because people tend not to start flailing until *after* they press the screen

    def stopGestureListen(self):
        if self.accelerometerPollFunc and self.accelerometerPollFunc.running:
            self.accelerometerPollFunc.stop()
        self._finishedAction()

    def _handleInput(self):
        """
        Handle currently available pygame input events.
        """
	
        time = pygame.time.get_ticks()
        self._updatePosition((time - self.previousTime)  /1000.0)
        self.previousTime = time

        #If player is pressing red self.BUTTON on scepter take two samples, add them to the average, match to predefined patterns
        #updated for lack of scepter button, replacement will be if player is pressing screen
        #don't know if this is the right way to get mouse buttokns from event queue

        for event in pygame.event.get():
            onDown = self._serialData[self.BUTTON] == 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._serialData[self.BUTTON] = 1
                if onDown:
                    self.startGestureListen()

            elif event.type == pygame.MOUSEBUTTONUP:
                self._serialData[self.BUTTON] = 0
                self.stopGestureListen()


            if (event.type == pygame.KEYDOWN):
                self.motionKeyPress(event.key)
            elif (event.type == pygame.KEYUP):
                self.motionKeyRelease(event.key)

        #buttons = pygame.mouse.get_pressed()
        #self._serialData[self.BUTTON] = buttons[0]
        #print str(self._serialData[self.BUTTON])

#        if self._serialData[self.BUTTON] == 1:
#            self._buildSampleData()
#            if self._sampleCnt == 2:
#                self._averageSampleData()
#                self._currentPattern = self._matchPattern()
#
#                if self._currentPattern != self._currentAction:
#                    self._actionQueue.append(self._currentPattern)
#                    if self._currentAction:
#                        self._finishedAction();
#
#        elif self._serialData[self.BUTTON] == 0 and self._currentPattern:
#            self._actionQueue = []
#            self._finishedAction()
#            #no action self.BUTTON pressed after matching a pattern; reset
#            self._currentPattern = None
#            #this could cause problems with unreliable serial connection, need to test
#            self._transitionAverages = self._initPattern(1)

        if (not self._currentAction) and self._actionQueue:
            self._startedAction(self._actionQueue.pop())

    def _matchPattern(self):
        bestFit = {
            ATTACK : self._patternDifference(self._transitionAverages, self._attack),
            UPGRADE : self._patternDifference(self._transitionAverages, self._upgrade),
            BUILD : self._patternDifference(self._transitionAverages, self._build),
            #SCAN : self._patternDifference(self._transitionAverages, self._scan),
        }

        # Returns the key (ATTACK, UPGRADE, etc) with the smallest value assigned
        return min(bestFit, key=bestFit.get)

    def _patternDifference(self,a,b):
        totalDifference = float(sys.maxint)
        for i in a.keys():
            for j in a[i].keys():
                totalDifference -= abs( a[i][j] - b[i][j] )
        totalDifference = sys.maxint - totalDifference
        return totalDifference

    def _buildSampleData(self):
        """
        reads the accelerometer and finds what area it's in.
        if the area is different from the last area checked, record the transition in self._sampleData
        """
        keys = ['x', 'y', 'z']
        data = self._readSerial()

        data = {'x': data[0], 'y': data[1], 'z': data[2]}
        results = {}
        for k in keys:
            if data[k] < self._areas[k][0]: results[k] = 0
            elif data[k] < self._areas[k][1]: results[k] = 1
            else: results[k] = 2
        currentPosition = (results['x'], results['y'], results['z'])
        if self._lastPosition != currentPosition:
            self._sampleData[self._lastPosition][currentPosition] += 1
            self._lastPosition = currentPosition
            self._sampleCnt += 1

    def _averageSampleData(self):
        """
        when two new transitions have been recorded by buildSampleData()
        this function takes self._tempData and averages it with self._sampleData
        """
        temp = self._sampleData
        for i in temp.keys():
            for j in temp[i].keys():
                self._sampleData[i][j] = temp[i][j] / float(self._sampleCnt)
        if self._transitionAverages:
            temp = deepcopy(self._transitionAverages)
            for i in temp.keys():
                for j in temp[i]:
                    self._transitionAverages[i][j] = ( temp[i][j] + self._sampleData[i][j] ) / 2.0
        #reset vars for buildSampleData()
        self._sampleData = self._initPattern(1)
        self._sampleCnt = 0


    def _readSerial(self):
        return self._ser.get_pos()


    def _initPattern(self,level):
        p = {}
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if level > 0:
                        p[i,j,k] = self._initPattern(level-1)
                    else:
                        p[i,j,k] = 0
        return p


    def _loadPattern(self,fileName):
        #with open(str(fileName), 'rb') as f:
        #    return pickle.load(f)
        try:
            f = open(str(fileName), 'rb')
            return pickle.load(f)
        finally:
            f.close()

    def motionKeyPress(self, key):
        if key == MOVE_UP:
            self._movingUp = True

        if key == MOVE_DOWN:
            self._movingDown = True

        if key == MOVE_LEFT:
            self._movingLeft = True

        if key == MOVE_RIGHT:
            self._movingRight = True


    def motionKeyRelease(self, key):
        if key == MOVE_UP:
            self._movingUp = False

        if key == MOVE_DOWN:
            self._movingDown = False

        if key == MOVE_LEFT:
            self._movingLeft = False

        if key == MOVE_RIGHT:
            self._movingRight = False

    def isMotionKey(self, key):
        return key == MOVE_UP or key == MOVE_DOWN or key == MOVE_LEFT or key == MOVE_RIGHT
