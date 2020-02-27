import pygame
import numpy as np
import time
import math
import random
from scipy import ndimage

from Colourise import gradient


DISPX = 600
DISPY = 600
RES = 6
ARRX = DISPX//RES
ARRY = DISPY//RES
FPS = 60

MAXAMP = 10
WAVEL = 10000000
WAVES = -10
FADE = 2000
TIMETAKEAWAY = 0.005

RAIN = True
RAINFREQ = 5

AUTOWAVEL = 75
AUTOPERIOD = .5
AUTOAMP = 5

STARTCOL = (200,100,105)
ENDCOL = (50,0,25)


class Wave():
    
    def __init__(self,pos,wavelength=AUTOWAVEL, period=AUTOPERIOD, amplitude=AUTOAMP):

        self.pos = pos
        self.wavelength = wavelength
        self.period = period
        self.amplitude = amplitude
        self.time = 0
        self.speed = self.wavelength/self.period
        self.done = False

    def draw(self, size, res):

        dismult = min( FADE/(self.speed*self.time+.001)**2 , 1 )-TIMETAKEAWAY
        if dismult<0:
            self.done = True
        
        dis = np.fromfunction( lambda x,y: np.hypot(x-self.pos[0],y-self.pos[1])*res,size)
        dis -= (self.time % self.period)/self.period*self.wavelength
        mult = np.fromfunction( lambda x,y:
               qurve( (np.hypot(x-self.pos[0],y-self.pos[1])-WAVES)*res -self.speed*self.time , WAVEL),
                size )
        
        amp = np.sin( dis/self.wavelength*2*math.pi )
        return  amp * self.amplitude * mult * dismult


class Draw():

    def __init__(self, sx,sy):

        self.mAArr = np.fromfunction( lambda x,y: np.arctan2(y-sy,x-sx), (2*sx,2*sy) )
        self.mDArr = np.fromfunction( lambda x,y: np.hypot(  y-sy,x-sx), (2*sx,2*sy) )

    def reflect( arr, mx,my ):

        sx,sy = arr.shape

        a =    self.mAArr[ sx-mx:2*sx-mx , sy-my:2*sy-my ]
        mdis = self.mDArr[ sx-mx:2*sx-mx , sy-my:2*sy-my ]

        sobelx = ndimage.sobel( arr, axis=0, mode='constant')[:,:,0]
        sobely = ndimage.sobel( arr, axis=1, mode='constant')[:,:,0]

        sobela = np.arctan2(sobely,sobelx)
        sobelm = np.hypot(sobelx,sobely)
        
        rela = np.abs(a-sobela)
        rela[rela>math.pi] = 2*math.pi - rela[rela>math.pi]
        intensity = ( math.pi - rela*2 ) / math.pi * 255
        intensity *= sobelm/3421.2
        disMult = .5-mdis /  1024
        disMult[disMult<0] = 0
        intensity *= disMult

        return intensity
        

def main():

    pygame.init()
    screen = pygame.display.set_mode( (DISPX,DISPY) )
    draw = Draw( DISPX,DISPY )

    waves = [ Wave( (0,0) )]
    loop( screen, draw, waves )


def loop( screen, draw, waves ):

    clock = pygame.time.Clock()

    while True:
        
        passed = clock.tick(FPS)

        if RAIN:
            waves.extend( genRain() )
        
        for w in waves:
            w.time += passed /1000
            if w.done == True:
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
        

    #arr = drawRoundMouse( arr, 100,100 )
    arr = ndimage.sobel( arr, axis=1, mode='constant' )

    arr*= 2/MAXAMP
    arr += .5
    arr[arr<0]=0
    arr[arr>1]=1

    return arr


def drawRoundMouse( arr, mx,my ):
    
    sobelx = ndimage.sobel( arr, axis=0, mode='constant')
    #sobely = ndimage.sobel( arr, axis=1, mode='constant')

    #sobela = np.arctan2(sobely,sobelx)
    #sobelm = np.hypot(sobelx,sobely)
    return sobelx


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
    return k/(n**4+k) # R -> (0,1) , bumpy middle

def curve(n,k):
    return n/(n+k) # R+ -> (0,1), 0 then positive gradient asymptote y=1



if __name__ == '__main__':
    main()





