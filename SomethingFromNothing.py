#SOF

from collections import defaultdict

import concurrent.futures
import math
import pygame
import random

#Set gravitational constant
ConstG = 1
#Set temporal step constant
dt = .001
dist = 100

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
        for idx,x in enumerate(lop):
            if x == (None, None):
                lop[idx] = (dist * random.uniform(-1,1), dist * random.uniform(-1,1))

        self._name      = name
        self._lop       = objlop(lop[0],lop[1],lop[2])
        self._mass      = mass
        self._radius    = radius
        self._density   = self._mass / ((4/3) * math.pi * (self._radius ** 3))
        self._mergelist = []

        
    #Calculate neighborhood affects of G and update acceleration
    def updateit(self,system):
        removeList       = []
        CollisionChkList = [self]
        
        #Calculate interactions between objects
        FTot = (0,0)
        
        for itemS in CollisionChkList:
            for itemO in system._listofobjs:
                #if item != self and not self._nextlopsource.count(item._name):
                if not CollisionChkList.count(itemO):
                    #Find rage and normalized directional vector from self to item
                    FoR     = tuple(map(lambda x, y: x - y, itemO._lop._x, itemS._lop._x))
                    Dist    = math.hypot(FoR[0],FoR[1])
                    FoRNorm = tuple(map(lambda x: x / Dist, FoR))
                
                    #If items do collide - update direction of first with force of
                    #  impact, mass, etc. and remove second from system.
                    if Dist <= itemS._radius + itemO._radius:
                    
                        #Calculate additional force from impact of item
                        self._lop._dx = tuple(map(lambda x, y: (itemO._mass * x + self._mass * y) / (itemO._mass + self._mass), itemO._lop._dx, self._lop._dx))
                            
                        #Update 'static' properties
                        self._mass   += itemO._mass
                        self._density = (self._density + itemO._density) / 2
                        self._radius  = ( (self._density / self._mass) * ((4/3) * math.pi) ) ** (-1/3)
                    
                        #Add collided items to checklist
                        CollisionChkList.append(itemO)

        for item in system._listofobjs:
            #if item != self and not self._nextlopsource.count(item._name):
            if not CollisionChkList.count(item):
                #Find rage and normalized directional vector from self to item
                FoR     = tuple(map(lambda x, y: x - y, item._lop._x, self._lop._x))
                Dist    = math.hypot(FoR[0],FoR[1])
                FoRNorm = tuple(map(lambda x: x / Dist, FoR))
                
                #If items do not collide - calculate force of gravity
                if Dist > self._radius + item._radius:
                    FoG  = ConstG * (self._mass * item._mass) / (Dist ** 2)
                    FTot = tuple(map(lambda x, y: FoG * x + y, FoRNorm, FTot))
                    
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
    for x in range(0,500): #Make n objects.
        p = ssobj(name = x, dx = (0, 0), ddx = (0, 0))
        sol._listofobjs.append(p)

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
            #    try:
            #        mergedObjs.extend(item.updateit(sol))
            #    except TypeError:
            #        item.updateit(sol)

            with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
                for item in sol._listofobjs: 
                    future = executor.submit(item.updateit, sol)
                    if not mergedObjs.count(item):
                        mergedObjs.extend(future.result())
            #        try:
            #            mergedObjs.extend(future.result())
            #        except TypeError:
            #            future.result()
            
            #Remove second obj.
            #mergedObjs = [item for item in mergedObjs if item is not None]
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


