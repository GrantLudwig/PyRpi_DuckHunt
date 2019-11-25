# File Name: duckHunt.py
# File Path: /home/ludwigg/Python/PyRpi_DuckHunt/duckHunt.py
# Run Command: sudo python3 /home/ludwigg/Python/PyRpi_DuckHunt/duckHunt.py

# Grant Ludwig
# 11/18/2019
# Duck Hunt

from graphics import *
from Duck import *
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO # Raspberry Pi GPIO library
import random
import math
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

kill = False

ducks = (   "/home/ludwigg/Python/PyRpi_DuckHunt/blueDuck.png",
            "/home/ludwigg/Python/PyRpi_DuckHunt/blackDuck.png",
            "/home/ludwigg/Python/PyRpi_DuckHunt/redDuck.png")
deadDucks = (   "/home/ludwigg/Python/PyRpi_DuckHunt/blueDuckDead.png",
                "/home/ludwigg/Python/PyRpi_DuckHunt/blackDuckDead.png",
                "/home/ludwigg/Python/PyRpi_DuckHunt/redDuckDead.png")
RoundDucks = []
ActiveDucks = []
duckIndex = 0

aim = Circle(Point(250, 250), 15)
innerAim = Circle(Point(250, 250), 5)
#target = Image(Point(0, 0), ducks[duckIndex])
#death = Image(Point(0, 0), deadDucks[duckIndex])
message = Text(Point(300, 100), "")
scoreText = Text(Point(100, 50), "")
roundText = Text(Point(100, 100), "")
ducksMissedText = Text(Point(100, 150), "")
shotsTakenText = Text(Point(100, 200), "")

NUM_DUCKS_PER_PERIOD = 2
NUM_PERIODS = 5
NUM_DUCKS_PER_ROUND = NUM_DUCKS_PER_PERIOD * NUM_PERIODS
TIME_TO_SHOOT = 6 # seconds
TIME_BETWEEN_DUCKS = 1 # seconds
TIME_BETWEEN_PERIODS = 1 # seconds
TIME_BETWEEN_ROUNDS = 1 # seconds
SHOTS_PER_PERIOD = 3
shotsTakenInPeriod = 0
roundNum = 0
currentPeriod = 1
totalScore = 0
roundScore = 0
ducksMissed = 0
timeAtLastPeriod = 0
lastPeriodSet = False
timeAtLastRound = 0
lastRoundSet = False
centerX = round(SCREEN_WIDTH / 2)
centerY = round(SCREEN_HEIGHT / 2)
unDrawDuck = []
kill = False

playing = False

win = GraphWin("Duck Hunt", SCREEN_WIDTH, SCREEN_HEIGHT, autoflush=False)

def getXPosition():
    global chan
    return round(chan.voltage/3.3 * SCREEN_WIDTH)

def getYPosition():
    global chan2
    return round(chan2.voltage/3.3 * SCREEN_HEIGHT)
    
def SetupRound():
    global ducks
    global RoundDucks
    global currentPeriod
    global roundScore
    global roundNum
    global lastRoundSet
    
    lastRoundSet = False
    currentPeriod = 1
    roundScore = 0
    roundNum += 1
    
    RoundDucks.clear()
    #randIndex = random.randint(0,len(ducks) - 1)
    for i in range(NUM_DUCKS_PER_ROUND):
        randIndex = random.randint(0,len(ducks) - 1)
        found = False
        while not found:
            tempDuck = Image(Point(random.randint(20, SCREEN_WIDTH - 20), random.randint(20, SCREEN_HEIGHT - 20)), ducks[randIndex])
            targetCenter = tempDuck.getAnchor()
            # TODO need to compute differently because not square screen
            if math.sqrt((250 - targetCenter.x)**2 + (250 - targetCenter.y)**2) <= (260):
                found = True
                RoundDucks.append(Duck(tempDuck, i, 10, 10))
    BeginPeriod()
    
def FlyAway():
    global unDrawDuck

    for duck in unDrawDuck:
        duck.FlyingAway = True
    
def SpawnDuck(index):
    global RoundDucks
    global ActiveDucks
    
    RoundDucks[index].duckGraphic().draw(win)
    RoundDucks[index].setActive()
    ActiveDucks.append(RoundDucks[index])
    
def BeginPeriod():
    global shotsTakenInPeriod
    global RoundDucks
    global ActiveDucks
    global lastPeriodSet
    
    lastPeriodSet = False
    index = 0
    shotsTakenInPeriod = 0
    duck = RoundDucks[index]
    # loop till non-activated duck is found
    while duck.isActivated():
        index += 1
        duck = RoundDucks[index]
    
    ActiveDucks.clear()
    for i in range(NUM_DUCKS_PER_PERIOD):
        SpawnDuck(index)
        index += 1
    
# returns True when period is done
def PeriodCheck():
    global ActiveDucks
    global timeAtLastPeriod
    global currentPeriod
    global lastPeriodSet
    global ducksMissed
    
    isADuckActive = False
    for duck in ActiveDucks:
        if duck.isActive():
            isADuckActive = True
    if not isADuckActive and not lastPeriodSet:
        for duck in ActiveDucks:
                if duck.isAlive():
                    ducksMissed += 1
                    unDrawDuck.append(duck)
                    FlyAway()
        timeAtLastPeriod = time.time()
        currentPeriod += 1
        lastPeriodSet = True
    return not isADuckActive
    
# returns true when round is done
def RoundCheck():
    global currentPeriod
    global timeAtLastRound
    global lastRoundSet
    global lastPeriodSet
    global unDrawDuck
    
    period = PeriodCheck()
    if currentPeriod > NUM_PERIODS:
        if not lastRoundSet:
            for duck in ActiveDucks:
                if duck.isAlive():
                    unDrawDuck.append(duck)
                    FlyAway()
            timeAtLastRound = time.time()
            lastRoundSet = True
            
        return True
    else:
        if period:
            if time.time() - timeAtLastPeriod >= TIME_BETWEEN_PERIODS and len(unDrawDuck) == 0:
                BeginPeriod()
        return False
    
def shoot(channel):
    global shotsTakenInPeriod
    global RoundDucks
    global roundScore
    global totalScore
    global playing
    global unDrawDuck
    
    if not playing:
        playing = True
    else:
        if shotsTakenInPeriod < SHOTS_PER_PERIOD:
            aimCenter = aim.getCenter()
            for target in ActiveDucks:
                targetCenter = target.duckGraphic().getAnchor()
                if math.sqrt((aimCenter.x - targetCenter.x)**2 + (aimCenter.y - targetCenter.y)**2) <= (30) and not target.FlyingAway:
                    target.killed()
                    unDrawDuck.append(target)
                    roundScore += 1
                    totalScore += 1
            shotsTakenInPeriod += 1

def main():
    global aim
    global innerAim
    global target
    global totalScore
    global unDrawDuck
    global playing
    global ActiveDucks
    
    # set coordnate plane for easy translation from the joystick position
    # xll, yll, xur, yur
    win.setCoords(SCREEN_WIDTH, 0, 0, SCREEN_HEIGHT)
    win.setBackground("Grey")
    
    message.setTextColor("white")
    message.setSize(20)
    message.draw(win)
    
    roundText.setTextColor("white")
    roundText.setSize(20)
    roundText.draw(win)
    
    scoreText.setTextColor("white")
    scoreText.setSize(20)
    scoreText.draw(win)
    
    ducksMissedText.setTextColor("white")
    ducksMissedText.setSize(20)
    ducksMissedText.draw(win)
    
    shotsTakenText.setTextColor("white")
    shotsTakenText.setSize(20)
    shotsTakenText.draw(win)
    
    #target.draw(win)
    #spawnTarget()
    
    aim.draw(win)
    innerAim.draw(win)
    
    dog = Image(Point(centerX,centerY), "/home/ludwigg/Python/PyRpi_DuckHunt/dog.png")
    
    SetupRound()
    while not playing: # need to press button to begin
        deathTime = 0 # need something so loop runs
    while(playing):
        #timeLeft = round(end - time.time(), 2)
        if ducksMissed >= 10:
            message.setText("Game Over!")
            scoreText.setText("Final Score: " + str(totalScore))
            dog.draw(win)
            playing = False
        else:
            #message.setText(timeLeft)
            scoreText.setText("Score: " + str(totalScore))
            roundText.setText("Round: " + str(roundNum))
            ducksMissedText.setText("Ducks Missed: " + str(ducksMissed))
            shotsTakenText.setText("Shots Left: " + str(SHOTS_PER_PERIOD - shotsTakenInPeriod))
            
            if RoundCheck():
                if time.time() - timeAtLastRound > TIME_BETWEEN_ROUNDS and len(unDrawDuck) == 0:
                    SetupRound()
            
            CanClear = True
            for unDraw in unDrawDuck:
                try:
                    #duckCenter = unDraw.duckGraphic().getAnchor()
                    if not unDraw.FlyingAway:
                        unDraw.duckGraphic().undraw()
                    
                    elif unDraw.duckGraphic().getAnchor().y > SCREEN_HEIGHT + 20:
                        unDraw.FlyingAway = False
                        unDraw.duckGraphic().undraw()
                    else:
                        unDraw.duckGraphic().move(0, 8)
                        CanClear = False
                except:
                    None
            if CanClear:
                unDrawDuck.clear()
                # death = Image(target.getAnchor(), deadDucks[duckIndex])
                # spawnTarget()
                # death.draw(win)
                # deathTime = time.time() + .5
            
                
            aim.undraw()
            innerAim.undraw()
            
            aim = Circle(Point(getXPosition(), getYPosition()), 15)
            innerAim = Circle(Point(getXPosition(), getYPosition()), 5)
            
            aim.setOutline("Red")
            innerAim.setFill("Red")
            
            aim.draw(win)
            innerAim.draw(win)
            
            for duck in ActiveDucks:
                if duck.isActive():
                    duckCenter = duck.duckGraphic().getAnchor()
                    if duckCenter.x >= SCREEN_WIDTH - 30:
                        duck.setVelocityX(-abs(duck.getRawVelocityX()))
                    elif duckCenter.x <= 30:
                        duck.setVelocityX(abs(duck.getRawVelocityX()))

                    if duckCenter.y >= SCREEN_HEIGHT - 30:
                        duck.setVelocityY(-abs(duck.getRawVelocityY()))
                    elif duckCenter.y <= 30:
                        duck.setVelocityY(abs(duck.getRawVelocityY()))
                        
                    duck.duckGraphic().move(duck.getVelocityX(), duck.getVelocityY())
            
            # if (deathTime - time.time()) < 0:
                # try:
                    # death.undraw()
                # except:
                    # print()
        update(60)
    
    time.sleep(5)
    win.close()

# Setup GPIO
GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(26, GPIO.IN)

GPIO.add_event_detect(26, GPIO.FALLING, callback=shoot, bouncetime=300)
	
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)
chan2 = AnalogIn(mcp, MCP.P1)

try:
    main()

except KeyboardInterrupt: 
    # This code runs on a Keyboard Interrupt <CNTRL>+C
    print('\n\n' + 'Program exited on a Keyboard Interrupt' + '\n') 

finally: 
    # This code runs on every exit and sets any used GPIO pins to input mode.
    GPIO.cleanup()