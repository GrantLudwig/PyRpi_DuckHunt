from graphics import *
import time
import random

class Duck:
    
    def __init__(self, DuckImage, Index, maxX, maxY, dict, window):
        self.__window = window
        self.__DuckImage = DuckImage
        self.__dict = dict
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
        self.__frameType = "up"
        self.__lastFrame = 1
        self.__frameNum = 0
        self.__animateTime = 0
        self.__TIME_TILL_NEXT_FRAME = 0.1
        self.__deathTime = 0
        self.__TIME_TILL_FALL = 0.5
        self.InDeath = False
        self.FlyingAway = False
        self.Spawning = True
        
    def setImageType(self, image):
        if self.__Active or self.FlyingAway or self.InDeath:
            if image == "normal":
                if self.__VelocityX >= 0 and self.__frameType != "left":
                    self.__frameType = "left"
                    center = self.__DuckImage.getAnchor()
                    try:
                        self.__DuckImage.undraw()
                    except:
                        None
                    self.__DuckImage = Image(center, self.__dict[self.__frameType][self.__frameNum])
                    self.__DuckImage.draw(self.__window)
                elif self.__VelocityX <= 0 and self.__frameType != "right":
                    self.__frameType = "right"
                    center = self.__DuckImage.getAnchor()
                    try:
                        self.__DuckImage.undraw()
                    except:
                        None
                    self.__DuckImage = Image(center, self.__dict[self.__frameType][self.__frameNum])
                    self.__DuckImage.draw(self.__window)
            elif image == "up":
                self.__frameType = "up"
                center = self.__DuckImage.getAnchor()
                try:
                    self.__DuckImage.undraw()
                except:
                    None
                self.__DuckImage = Image(center, self.__dict[self.__frameType][self.__frameNum])
                self.__DuckImage.draw(self.__window)
            elif image == "down":
                self.__frameType = "down"
                center = self.__DuckImage.getAnchor()
                try:
                    self.__DuckImage.undraw()
                except:
                    None
                self.__DuckImage = Image(center, self.__dict[self.__frameType])
                self.__DuckImage.draw(self.__window)
            elif image == "shot":
                self.__frameType = "shot"
                center = self.__DuckImage.getAnchor()
                try:
                    self.__DuckImage.undraw()
                except:
                    None
                self.__DuckImage = Image(center, self.__dict[self.__frameType])
                self.__DuckImage.draw(self.__window)
        
    def animate(self):
        if time.time() - self.__animateTime >= self.__TIME_TILL_NEXT_FRAME and self.__Alive:
            if self.__frameNum == 0:
                self.__frameNum = 1
                self.__lastFrame = 0
            elif self.__frameNum == 2:
                self.__frameNum = 1
                self.__lastFrame = 2
            elif self.__lastFrame == 2:
                self.__frameNum = 0
            else:
                self.__frameNum = 2
            
            if self.__frameType != "shot" or self.__frameType != "down":
                center = self.__DuckImage.getAnchor()
                try:
                    self.__DuckImage.undraw()
                except:
                    None
                self.__DuckImage = Image(center, self.__dict[self.__frameType][self.__frameNum])
                self.__DuckImage.draw(self.__window)
            else:
                center = self.__DuckImage.getAnchor()
                try:
                    self.__DuckImage.undraw()
                except:
                    None
                self.__DuckImage = Image(center, self.__dict[self.__frameType])
                self.__DuckImage.draw(self.__window)
            
            self.__animateTime = time.time()

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
            self.setImageType("normal")
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
        self.setImageType("normal")
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
        
    def death(self):
        center = self.__DuckImage.getAnchor()
        if center.y < 100 or not self.InDeath:
            self.InDeath = False
            return True
        else:
            if time.time() - self.__deathTime >= self.__TIME_TILL_FALL:
                if self.__frameType != "down":
                    self.setImageType("down")
                #self.animate()
                self.__DuckImage.move(0, -10)
            else:
                if self.__frameType != "shot":
                    self.setImageType("shot")
                #self.animate()
                self.__DuckImage.move(0, 0)
            return False
        
    def setActive(self):
        self.__ActiveTime = time.time()
        self.__animateTime = time.time()
        self.__VelocitySetTime = time.time()
        self.__Active = True
        self.__Activated = True
        
    def killed(self):
        self.__Alive = False
        self.__Active = False
        self.FlyingAway = False
        self.InDeath = True
        self.__deathTime = time.time()
        
    def gotAway(self):
        self.InDeath = False