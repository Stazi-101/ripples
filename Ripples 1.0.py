import pygame
import numpy as np
import time
import math
import random

from Colourise import gradient

DISPX = 600
DISPY = 600
RES = 4
ARRX = DISPX//RES
ARRY = DISPY//RES
FPS = 60

MAXAMP = 10
WAVEL = 500
WAVES = -7
FADE = 5000

RAIN = True
RAINFREQ = 4

AUTOWAVEL = 100
AUTOPERIOD = .4
AUTOAMP = 5

STARTCOL = (200,100,105)
ENDCOL = (50,0,100)

class Wave():
    
    def __init__(self,pos,wavelength=AUTOWAVEL, period=AUTOPERIOD, amplitude=AUTOAMP):

        self.pos = pos
        self.wavelength = wavelength
        self.period = period
        self.amplitude = amplitude
        self.time = 0
        self.speed = self.wavelength/self.period

    def draw(self, size, res):
        
        dis = np.fromfunction( lambda x,y: np.hypot(x-self.pos[0],y-self.pos[1])*res,size)
        dis -= (self.time % self.period)/self.period*self.wavelength
        mult = np.fromfunction( lambda x,y:
               qurve( (np.hypot(x-self.pos[0],y-self.pos[1])-WAVES)*res -self.speed*self.time , WAVEL),
                size )
        dismult = min( FADE/(self.speed*self.time)**2 , 1 )
        amp = np.sin( dis/self.wavelength*2*math.pi )
        return  amp * self.amplitude * mult * dismult

# self.speed*self.passedv
#amp*self.amplitude


def main():

    pygame.init()
    screen = pygame.display.set_mode( (DISPX,DISPY) ) 

    waves = [ Wave( (0,0) )]
             #Wave( (100,200), 20, 2, 2)]

    loop( screen, waves )


def loop( screen, waves ):

    clock = pygame.time.Clock()

    while True:
        
        passed = clock.tick(FPS)

        if RAIN:
            waves.extend( genRain() )
        
        for w in waves:
            w.time += passed /1000
            if w.time > max( (DISPX,DISPY) )/w.speed*2:
                waves.remove(w)
        
        drawArr( screen, genArr(waves) )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                waves.append( Wave( (mx/RES,my/RES) ) )
 

def genArr(waves):
    
    arr = np.zeros( (ARRX,ARRY) )

    for w in waves:
        arr += w.draw( (ARRX,ARRY), RES )
    '''
    maxW = sum([ w.amplitude for w in waves]) 
    maxW = maxW if maxW else 1
    '''
    arr*= 2/MAXAMP
    arr += .5
    arr[arr<0]=0
    arr[arr>1]=1
    
    '''arr *= 31
    if np.amax(arr)>255:
        print(np.amax(arr))'''

    return arr


def drawArr( screen, arr ):

    arr = gradient( arr, STARTCOL, ENDCOL )

    surfarray = pygame.surfarray.pixels3d(screen)
    surfarray[ :,:,: ] = np.repeat( np.repeat(arr,RES,axis=0), RES, axis=1 )
    del surfarray

    pygame.display.update()


def genRain():

    if random.random() < RAINFREQ/FPS:
        return [ Wave( (random.random()*ARRX, random.random()*ARRY) ) ]

    return []
                       


def qurve(n,k):
    return k/(n**2+k) # R -> (0,1) , bumpy middle

def curve(n,k):
    return n/(n+k) # R+ -> (0,1), 0 then positive gradient asymptote y=1



if __name__ == '__main__':
    main()





