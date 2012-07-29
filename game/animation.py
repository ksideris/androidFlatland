#from twisted.internet.task import LoopingCall
import pygame
import itertools
import math,time
from vector import Vector2D

rotateForTablet = True

def _loadImage(path):
    image = pygame.image.load(path)
    if rotateForTablet:
        image = pygame.transform.rotate(image, -90)
        
    # TODO Are all of our images alpha'd now?
    if True:
        image = image.convert_alpha()
    else:
        image = image.convert()
        image.set_colorkey(image.get_at((0,0)))
    return image

class Image(object):
    def __init__(self, path, offset = (0,0)):
        
        ox = offset[0]
        oy = offset[1]
        if rotateForTablet:
            ox = offset[1]
            oy = offset[0]
 
        
        if path:
            self.path = path.path
        self.offset = Vector2D(ox, oy)
        self.degrees = None

    def addExistingImage(self,image):
        self._image=image
        self._setCenter()
    def load(self):
        self._image = _loadImage(self.path)
        self._setCenter()




    def _setCenter(self):
        self.center = Vector2D(self._image.get_rect().center)
        self.width, self.height = self._image.get_rect().size

    def draw(self, screen, position):
        if self.degrees == None:
            imagePosition = position - self.center + self.offset
            screen.blit(self._image, imagePosition)
        else:
            imagePosition = position - self.center + self.offset
            image = pygame.transform.rotate(self._image, float(self.degrees))
            screen.blit(image, imagePosition)

    def drawScaled(self, screen, position, scale):
        center = self.center * scale
        
        center.x = math.ceil(center.x)
        center.y = math.ceil(center.y)
        
        #print str(center.x) + ", " + str(center.y) + "\n"
        size = Vector2D(int(math.ceil(2*center.x)), int(math.ceil(2*center.y)))
        
        
        
        image = pygame.transform.smoothscale(self._image, size)
        imagePosition = (position[0] - center[0], position[1] - center[1])
        screen.blit(image, imagePosition)

    def copy(self):
        return self
    
    def setRotation(self, degrees):
        self.degrees = degrees
        
class Animation(Image):
    def load(self):
        i = 1
        self._images = []
        while True:
            try:
                self._images.append(_loadImage(self.path % (i, )))
                i += 1
            except Exception:
                break
        self._image = self._images[0]
        self._setCenter()

    '''def start(self, fps):
        self._loopingCall = LoopingCall(self._nextImage, iter(self._images))
        return self._loopingCall.start(1.0 / fps)

    def startReversed(self, fps):
        self._loopingCall = LoopingCall(self._nextImage, reversed(self._images))
        return self._loopingCall.start(1.0 / fps)

    def stop(self):
        self._loopingCall.stop()

    def _nextImage(self, iterator):
        try:
            self._image = iterator.next()
        except StopIteration:
            self.stop()'''

    def start(self,fps,end):
        self.animationCounter = 0 
        self.fps =fps
        self.animationLastFired =time.time()
        self.animationEnd = end

    def getImage(self,i):
        im = Image(None)
        im.addExistingImage(self._images[i])
        return im

    def update(self):
        if(self.animationCounter>= self.animationEnd):
	        self.animationCounter = 0 
	        self.animationLastFired = 0 
	        return None
        else:
	        im = self.getImage(self.animationCounter)
	        print self.animationCounter,self.animationLastFired,time.time()-  self.animationLastFired
	        if(time.time()-  self.animationLastFired>self.fps ):
	            self.animationCounter+=1
	            print self.animationCounter,self.animationLastFired
	            self.animationLastFired = time.time()
	        return im


    def copy(self):
        animation = Animation(None)
        animation.center = self.center
        animation._images = self._images
        animation.offset = self.offset
        return animation
    
#    def setRotation(self, degrees):
#        for i in self._images:
#            i.setRotation(degrees)
        
class LoopingAnimation(Animation):
    def start(self, fps):
        #self._loopingCall = LoopingCall(self._nextImage, itertools.cycle(self._images))
        #return self._loopingCall.start(1.0 / fps)
		pass
    def _nextImage(self, iterator):
        try:
            self._image = iterator.next()
        except StopIteration:
            self.stop()
