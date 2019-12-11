from graphics import *
import time
import random

class Duck:
    # Variables
    # ---------
    # private Image DuckImage
    # private int index // index in round of ducks
    # private bool Alive
    # private bool Active
    # private Time ActiveTime
    # private int TIME_TO_SHOOT
    # private float TIME_TILL_NEW_VELOCITY
    # private int VelocityX
    # private int VelocityY
    # private Time VelocitySetTime
    
    def __init__(self, DuckImage, Index, maxX, maxY):
        self.__DuckImage = DuckImage
        self.Index = Index
        self.__Alive = True
        self.__Active = False
        self.__Activated = False
        self.__ActiveTime = None
        self.__TIME_TO_SHOOT = 6.2
        self.__TIME_TILL_NEW_VELOCITY = 0.5
        self.__MaxX = maxX
        self.__MaxY = maxY
        self.__VelocityX = random.randint(-maxX,maxX)
        self.__VelocityY = random.randint(-maxY,maxY)
        self.__VelocitySetTime = None
        self.FlyingAway = False
        self.Spawning = True
        
    def getVelocityX(self):
        if time.time() - self.__VelocitySetTime >= self.__TIME_TILL_NEW_VELOCITY:
            # set VelocityX
            self.__VelocityX = random.randint(-self.__MaxX,self.__MaxX)
            while self.__VelocityX == 0:
                self.__VelocityX = random.randint(-self.__MaxX,self.__MaxX)
            # set VelocityY
            self.__VelocityY = random.randint(-self.__MaxY,self.__MaxY)
            while self.__VelocityY == 0:
                self.__VelocityY = random.randint(-self.__MaxY,self.__MaxY)
            # reset time
            self.__VelocitySetTime = time.time()
            return self.__VelocityX
        else:
            return self.__VelocityX
            
    def getVelocityY(self):
        if time.time() - self.__VelocitySetTime >= self.__TIME_TILL_NEW_VELOCITY:
            # set VelocityX
            self.__VelocityX = random.randint(-self.__MaxX,self.__MaxX)
            while self.__VelocityX == 0:
                self.__VelocityX = random.randint(-self.__MaxX,self.__MaxX)
            # set VelocityY
            self.__VelocityY = random.randint(-self.__MaxY,self.__MaxY)
            while self.__VelocityY == 0:
                self.__VelocityY = random.randint(-self.__MaxY,self.__MaxY)
            # reset time
            self.__VelocitySetTime = time.time()
            return self.__VelocityY
        else:
            return self.__VelocityY
            
    def getRawVelocityX(self):
        return self.__VelocityX
        
    def getRawVelocityY(self):
        return self.__VelocityY
        
    def setVelocityX(self, value):
        self.__VelocityX = value
        
    def setVelocityY(self, value):
        self.__VelocityY = value
        
    def duckGraphic(self):
        return self.__DuckImage
        
    def isActive(self):
        if time.time() - self.__ActiveTime >= self.__TIME_TO_SHOOT:
            self.__Active = False
        return self.__Active
        
    def isAlive(self):
        return self.__Alive
        
    def isActivated(self):
        return self.__Activated
        
    def setActive(self):
        self.__ActiveTime = time.time()
        self.__VelocitySetTime = time.time()
        self.__Active = True
        self.__Activated = True
        
    def killed(self):
        self.__Alive = False
        self.__Active = False
        self.FlyingAway = False