#SOF

from collections import defaultdict

import math
import pygame
import random

#Set gravitational constant
ConstG = 1
#Set temporal step constant
dt = .01
dist = 100

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
                 mass   = 1000):

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

        #Save next updates and flag if already calculated
        self._nextlopsource = []
        self._nextlop       = objlop((0,0),(0,0),(0,0))

    #Calculate neighborhood affects of G and update acceleration
    def updateit(self,system):
        FTot = (0,0)
        #Each calculation is performed twice - this could be improved by saving
        # calculated forces in both objects when it is calculated for the first.
        for item in system._listofobjs:
            if item != self and not self._nextlopsource.count(item._name):
                #Find rage and normalized directional vector from self to item
                FoR     = tuple(map(lambda x, y: x - y, item._lop._x, self._lop._x))
               # print(FoR)
                Dist    = math.hypot(FoR[0],FoR[1])
                FoRNorm = tuple(map(lambda x: x / Dist, FoR))

                #If items do not collide - calculate force of gravity
                if Dist > self._radius + item._radius:
                    FoG  = ConstG * (self._mass * item._mass) / (Dist ** 2)
                    #self._neighbors.append([FoRx, FoRy, Dist, FoG])
                    FTot = tuple(map(lambda x, y: FoG * x + y, FoRNorm, FTot))

                    item._nextlopsource.append(self._name)
                    item._nextlop._ddx = tuple(map(lambda x, y: 
                        -FoG * x / item._mass + y, FoRNorm, item._nextlop._ddx))

                #If items do collide - update direction of first with force of
                #  impact, mass, etc. and remove second from system.
                else:
                    #Calculate additional force from impact of item
                    self._lop._dx = tuple(map(lambda x, y: 
                        (item._mass * x + self._mass * y) / (item._mass + self._mass), item._lop._dx, self._lop._dx))
                        
                    #Update 'static' properties
                    self._mass   += item._mass
                    self._density = (self._density + item._density) / 2
                    self._radius  = ( (self._density / self._mass) * ((4/3) * math.pi) ) ** (-1/3)

                    #Remove second obj.
                    system._listofobjs.remove(item)
            else:
                pass
        #Move object and update acceleration
        self.moveit()
        self._lop._ddx = tuple(map(lambda x, y:
            x + y / self._mass, item._nextlop._ddx, FTot))
        item._nextlopsource = []
        item._nextlop._ddx = (0,0)

    #Move the object within the solar system
    def moveit(self):
        self._lop._x  = tuple(map(lambda x,y,z: 
            x + y * dt + (z * dt**2) / 2, self._lop._x, self._lop._dx, self._lop._ddx))
        self._lop._dx = tuple(map(lambda y,z: 
            y + z * dt, self._lop._dx, self._lop._ddx))

## Visual output
def RunGraphics():
    #Make Solar System           
    sol = solarsystem()
    #big = ssobj(name = -1, x = (0,0), dx = (0, 0), ddx = (0, 0), radius = .1, mass = 10000)
    #sol._listofobjs.append(big)
    for x in range(0,100): #Make n objects.
        p = ssobj(name = x, dx = (0, 0), ddx = (0, 0))
        sol._listofobjs.append(p)

    keysPressed = defaultdict(bool)
    bClearScreen = True
    
    pygame.init()
    win=pygame.display.set_mode((1200,900))
    pygame.display.set_caption('Plasma Simulation - Press ESC to Exit')
    
    #Detect user inputs
    def ScanKeyboard():
        event = pygame.event.poll()
        if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            keysPressed[event.key] = event.type == pygame.KEYDOWN

    while True:
        pygame.display.flip()
        if bClearScreen:
            win.fill((0,0,0))
        #win.lock()
        for item in sol._listofobjs:
            #if item._name == -1:
            #    pygame.draw.circle(win,
            #                   (255,0,0),
            #                   (int(round(600 + 100 * item._lop._x[0])),int(round(450 + 100 * item._lop._x[1]))),
            #                   int(round(2 * item._radius)),
            #                   0)
            #else:
                pygame.draw.circle(win,
                                   (255,255,255),
                                   (int(round(600 + item._lop._x[0])),int(round(450 + item._lop._x[1]))),
                                   int(round(item._radius)),
                                   0)
        #win.unlock()
        ScanKeyboard()
        
        for item in sol._listofobjs:
            item.updateit(sol)

        if keysPressed[pygame.K_ESCAPE]:
            pygame.quit()
            break
        
        if keysPressed[pygame.K_SPACE]:
            while keysPressed[pygame.K_SPACE]:
                ScanKeyboard()
            bClearScreen = not bClearScreen

if __name__ == "__main__":
    RunGraphics()


