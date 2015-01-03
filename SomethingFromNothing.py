#SOF

from collections import defaultdict

import concurrent.futures
import math
import pygame
import random

#Set gravitational constant
ConstG = 1
#Set temporal step constant
dt = .01
dist = 200

class BreakOut(Exception): pass

#Solar System Properties
class solarsystem:
    def __init__(self):
        self._listofobjs = []

#Lost of Solar System Object Position and Movement Properties
class objlop:
    def __init__(self,x,dx,ddx):
        self._x   = x
        self._dx  = dx
        self._ddx = ddx

#Solar System Object (e.g. planet)
class ssobj:
    global ConstG
    global dt
    global dist
    
    #Initialize solar system object location, velocity and acceleration
    #  as well as other properties (density, radius, etc.)
    def __init__(self, name,
                 x      = (None, None),
                 dx     = (None, None),
                 ddx    = (None, None),
                 radius = .5,
                 mass   = 10):

        lop = [x,dx,ddx]
        for idx, x in enumerate(lop):
            if x == (None, None):
                phi = random.uniform(0, 2 * math.pi)
                r   = dist * random.uniform(0,1)
                
                lop[idx] = (r * math.cos(phi), r * math.sin(phi))

        self._name      = name
        self._lop       = objlop(lop[0],lop[1],lop[2])
        self._mass      = mass
        self._radius    = radius
        self._density   = self._mass / ((4/3) * math.pi * (self._radius ** 3))
        self._mergelist = []
        
    #Calculate neighborhood geometry
    def neighborhood(self, system):
        #Initialize NH
        self._NHDist    = {}
        self._NHVect    = {}
        
        for item in system._listofobjs:
            if item != self:
                #Find rage and normalized directional vector from self to item
                FoR     = tuple(map(lambda x, y: x - y, item._lop._x, self._lop._x))
                Dist    = math.hypot(FoR[0],FoR[1])
                FoRNorm = tuple(map(lambda x: x / Dist, FoR))
            
                #Save calculated values
                self._NHDist[item._name] = Dist
                self._NHVect[item._name] = FoRNorm
        
    #Calculate neighborhood affects of G and update acceleration
    def updateit(self,system):
        CollisionChkList = [self]
        
        #Calculate interactions between objects (collisions)
        FTot = (0,0)
        for itemS in CollisionChkList:
            for itemO in system._listofobjs:
                #if item != self and not self._nextlopsource.count(item._name):
                if not CollisionChkList.count(itemO):
                    #If items do collide - update direction of first with force of
                    #  impact, mass, etc. and remove second from system.
                    if itemS._NHDist[itemO._name] <= itemS._radius + itemO._radius:
                    
                        #Calculate additional force from impact of item
                        self._lop._dx = tuple(map(lambda x, y: (itemO._mass * x + self._mass * y) / (itemO._mass + self._mass), itemO._lop._dx, self._lop._dx))
                            
                        #Update 'static' properties
                        self._mass   += itemO._mass
                        self._density = (self._density + itemO._density) / 2
                        self._radius  = ( (self._density / self._mass) * ((4/3) * math.pi) ) ** (-1/3)
                    
                        #Add collided items to checklist
                        CollisionChkList.append(itemO)

        #Calculate interactions between objects (gravity)
        for item in system._listofobjs:
            #if item != self and not self._nextlopsource.count(item._name):
            if not CollisionChkList.count(item):                

                #If items do not collide - calculate force of gravity
                if self._NHDist[item._name] > self._radius + item._radius:
                    FoG  = ConstG * (self._mass * item._mass) / (self._NHDist[item._name] ** 2)
                    FTot = tuple(map(lambda x, y: FoG * x + y, self._NHVect[item._name], FTot))
                    
        #Move object and update acceleration
        self.moveit(FTot)
        CollisionChkList.remove(self)
        return CollisionChkList
        
    #Move the object within the solar system
    def moveit(self, FTot):
        self._lop._ddx = FTot
        #self._lop._ddx = tuple(map(lambda x, y:    x + y, self._nextlop._ddx, FTot))
        self._lop._dx  = tuple(map(lambda y, z:    y + z * dt, self._lop._dx, self._lop._ddx))
        self._lop._x   = tuple(map(lambda x, y, z: x + y * dt + (z * dt**2) / 2, self._lop._x, self._lop._dx, self._lop._ddx))
        
    
    def displayit(self,disp):
        pygame.draw.circle(disp,
                           (255,255,255), 
                           (int(round(600 + self._lop._x[0])),int(round(450 + self._lop._x[1]))),
                           int(round(self._radius)),
                           0)

## Visual output
def RunGraphics():
    
    #Make Solar System           
    sol = solarsystem()
    with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:
        for x in range(0,250): #Make n objects.
            futureObj = executor.submit(ssobj,name = x, dx = (0, 0), ddx = (0, 0))
            sol._listofobjs.append(futureObj.result())

    #Initialize Keyboard Inputs
    keysPressed = defaultdict(bool)
    bClearScreen = True
    
    #Initialize pygame Window
    pygame.init()
    win = pygame.display.set_mode((1200,900))
    pygame.display.set_caption('Plasma Simulation - Press ESC to Exit')
    
    #Run game and detect user inputs
    try:
        while True:
            pygame.display.flip()
            
            if bClearScreen:
                win.fill((0,0,0))
            
            mergedObjs = []
            for item in sol._listofobjs: 
                item.displayit(win)
                
            with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:
                for item in sol._listofobjs: 
                    futureNH = executor.submit(item.neighborhood, sol)
                    futureNH.result()
                    
            with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:
                for item in sol._listofobjs: 
                    futureMv = executor.submit(item.updateit, sol)
                    if not mergedObjs.count(item):
                        mergedObjs.extend(futureMv.result())
            
            #Remove second obj.
            try:
                for item in mergedObjs:
                    try:
                        sol._listofobjs.remove(item)
                    except ValueError:
                        pass
            except TypeError:
                pass
        
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                    keysPressed[event.key] = event.type == pygame.KEYDOWN
                if keysPressed[pygame.K_ESCAPE] or event.type == pygame.QUIT:
                    raise BreakOut
                if keysPressed[pygame.K_SPACE]:
                    bClearScreen = not bClearScreen
    except BreakOut:                
        pygame.quit()
        
if __name__ == "__main__":
    RunGraphics()


