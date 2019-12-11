# File Name: duckHunt.py
# File Path: /home/ludwigg/Python/PyRpi_DuckHunt/duckHunt.py
# Run Command: sudo python3 /home/ludwigg/Python/PyRpi_DuckHunt/duckHunt.py

# Grant Ludwig
# 11/18/2019
# Duck Hunt
# Note: Due to time constraints, the code is not as pretty as it should
    # This should all get refactored to be more legiable as well as to proably run faster
    # Overall this is very much spaghetti code

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
import threading

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

kill = False

ducks = (   "/home/ludwigg/Python/PyRpi_DuckHunt/blueDuck.png",
            "/home/ludwigg/Python/PyRpi_DuckHunt/blackDuck.png",
            "/home/ludwigg/Python/PyRpi_DuckHunt/redDuck.png")
deadDucks = (   "/home/ludwigg/Python/PyRpi_DuckHunt/blueDuckDead.png",
                "/home/ludwigg/Python/PyRpi_DuckHunt/blackDuckDead.png",
                "/home/ludwigg/Python/PyRpi_DuckHunt/redDuckDead.png")
background = "/home/ludwigg/Python/PyRpi_DuckHunt/DuckHuntBackground.png"
bulletImage = "/home/ludwigg/Python/PyRpi_DuckHunt/bullet.png"
duckCountAliveImage = "/home/ludwigg/Python/PyRpi_DuckHunt/whiteDuck.png"
duckCountDeadImage = "/home/ludwigg/Python/PyRpi_DuckHunt/deadRedDuck.png"
menuSelect = "/home/ludwigg/Python/PyRpi_DuckHunt/MenuSelection.png"
menuSelected = "/home/ludwigg/Python/PyRpi_DuckHunt/SelectedMenuSelection.png"

RoundDucks = []
ActiveDucks = []
duckIndex = 0

GPIO_A = 12
GPIO_B = 13
GPIO_C = 6
GPIO_D = 16
GPIO_E = 17
GPIO_F = 27
GPIO_G = 7
GPIO_D1 = 22
GPIO_D2 = 25
GPIO_D3 = 24
GPIO_D4 = 23
GPIO_COLON = 8

NUM_DUCKS_PER_PERIOD = 2
NUM_PERIODS = 5
NUM_DUCKS_PER_ROUND = NUM_DUCKS_PER_PERIOD * NUM_PERIODS
TIME_TO_SHOOT = 6 # seconds
TIME_BETWEEN_DUCKS = 1 # seconds
TIME_BETWEEN_PERIODS = 1 # seconds
TIME_BETWEEN_ROUNDS = 1 # seconds
SHOTS_PER_PERIOD = 3
MAX_ROUNDS = 999
EASY_RADIUS = 100
NORMAL_RADIUS = 50
HARD_RADIUS = 30
aimRadius = EASY_RADIUS

aim = Circle(Point(0, 0), aimRadius)
innerAim = Circle(Point(0, 0), 5)
#target = Image(Point(0, 0), ducks[duckIndex])
#death = Image(Point(0, 0), deadDucks[duckIndex])
message = Text(Point(300, 100), "")
scoreText = Text(Point(117, 30), "")
roundText = Text(Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), "")
ducksMissedText = Text(Point(100, 150), "")
shotsTakenText = Text(Point(SCREEN_WIDTH - 62, 40), "")

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
bullets = []
kill = False
roundNumText = "000"
duckDisplay = []
deadDuckDisplay = []
indexKilledDucks = [] # will have 2 indexs, the index of the current ducks
menuSelection = 0
difficultySelection = 0
diffSelected = False
quit = False

clockOutputLock = threading.Lock()

# A B C D E F G
numberMap = {" ":(0,0,0,0,0,0,0),
			"0":(1,1,1,1,1,1,0),
			"1":(0,1,1,0,0,0,0),
			"2":(1,1,0,1,1,0,1),
			"3":(1,1,1,1,0,0,1),
			"4":(0,1,1,0,0,1,1),
			"5":(1,0,1,1,0,1,1),
			"6":(1,0,1,1,1,1,1),
			"7":(1,1,1,0,0,0,0),
			"8":(1,1,1,1,1,1,1),
			"9":(1,1,1,1,0,1,1)}
            
CLOCK_OUTPUT_SIZE = 4
clockOutput = "0000"

playing = False

win = GraphWin("Duck Hunt", SCREEN_WIDTH, SCREEN_HEIGHT, autoflush=False)

# setup bullets
for i in range(SHOTS_PER_PERIOD):
    bullets.append(Image(Point(SCREEN_WIDTH - (32 + (30 * i)), 22), bulletImage))
    
# setup duck display
for i in range(NUM_DUCKS_PER_ROUND):
    duckDisplay.append(Image(Point(SCREEN_WIDTH - (247 + (30 * i)), 30), duckCountAliveImage))
    deadDuckDisplay.append(Image(Point(SCREEN_WIDTH - (247 + (30 * i)), 30), duckCountDeadImage))

def getXPosition():
    global chan2
    return round((1 - (chan2.voltage/3.3)) * SCREEN_WIDTH)

def getYPosition():
    global chan
    # 333 is the height of the shootable area, + 117 to offset from bottom of screen
    return round((chan.voltage/3.3 * 333) + 117)
    
def getRawY():
    global chan
    return chan.voltage/3.3
    
def UpdateRoundText(num):
    global roundNumText
    temp = ""
    for i in range(len(str(MAX_ROUNDS)) - len(str(num))):
        temp += "0"
    temp += str(num)
    roundNumText = temp
    roundText.setText("Round: " + roundNumText)
    
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
    UpdateRoundText(roundNum)
    
    RoundDucks.clear()
    #randIndex = random.randint(0,len(ducks) - 1)
    for i in range(NUM_DUCKS_PER_ROUND):
        randIndex = random.randint(0,len(ducks) - 1)
        # found = False
        # while not found:
        tempDuck = Image(Point(random.randint(20, SCREEN_WIDTH - 20), random.randint(118, SCREEN_HEIGHT - 30)), ducks[randIndex])
        targetCenter = tempDuck.getAnchor()
        RoundDucks.append(Duck(tempDuck, i, 10, 10))
            # TODO need to compute differently because not square screen
            # if math.sqrt(((SCREEN_WIDTH / 2) - targetCenter.x)**2 + (250 - targetCenter.y)**2) <= (260):
                # found = True
                # RoundDucks.append(Duck(tempDuck, i, 10, 10))
    for duck in duckDisplay:
        try:
            duck.draw(win)
        except:
            None
    BeginPeriod()
    
def FlyAway():
    global unDrawDuck

    for duck in unDrawDuck:
        duck.FlyingAway = True
    
def SpawnDuck(index):
    global RoundDucks
    global ActiveDucks
    
    if index > 1:
        RoundDucks[index].duckGraphic().draw(win)
    RoundDucks[index].setActive()
    ActiveDucks.append(RoundDucks[index])
    
def BeginPeriod():
    global shotsTakenInPeriod
    global RoundDucks
    global ActiveDucks
    global lastPeriodSet
    global bullets
    global indexKilledDucks
    
    indexKilledDucks.clear()
    
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
        indexKilledDucks.append(index)
        index += 1
        
    # spawn bullets
    for bullet in bullets:
        try:
            bullet.draw(win)
        except:
            None
    
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
    global menuSelection
    global quit
    global difficultySelection
    global diffSelected
    global aimRadius
    global ActiveDucks
    
    if not playing:
        if menuSelection == 0:
            playing = True
        elif menuSelection == 1:
            # settings
            None
        else:
            playing = True
            quit = True
            
    elif playing and not diffSelected:
        if difficultySelection == 0:
            aimRadius = EASY_RADIUS
            diffSelected = True
        elif difficultySelection == 1:
            aimRadius = NORMAL_RADIUS
            diffSelected = True
        else:
            aimRadius = HARD_RADIUS
            diffSelected = True
            
    else:
        if shotsTakenInPeriod < SHOTS_PER_PERIOD:
            aimCenter = aim.getCenter()
            for target in ActiveDucks:
                targetCenter = target.duckGraphic().getAnchor()
                if math.sqrt((aimCenter.x - targetCenter.x)**2 + (aimCenter.y - targetCenter.y)**2) <= (aimRadius + 5) and not target.FlyingAway and target.isAlive():
                    unDrawDuck.append(target)
                    target.killed()
                    roundScore += 1
                    totalScore += 1
            shotsTakenInPeriod += 1
            
def reset(channel):
    print("TEST")
            
def updateScore():
    global clockOutput
    global totalScore
    
    if int(clockOutput) != totalScore:
        temp = ""
        for i in range(CLOCK_OUTPUT_SIZE - len(str(totalScore))):
            temp += "0"
        temp += str(totalScore)
        clockOutputLock.acquire()        
        clockOutput = temp
        clockOutputLock.release()
            
def scoreLoop():
    global numberMap
    global clockOutput
    global segments
    global digits
    
    GPIO.setwarnings(False) # Ignore warnings
    GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
    
    while(True):
        if not clockOutputLock.locked():
            for i in range(len(digits)):
                for j in range(len(segments)):
                    GPIO.output(segments[j], numberMap[clockOutput[i]][j])
                GPIO.output(digits[i], 0)
                time.sleep(0.001)
                GPIO.output(digits[i], 1)

def main():
    global aim
    global innerAim
    global target
    global totalScore
    global roundScore
    global unDrawDuck
    global playing
    global ActiveDucks
    global ducksMissed
    global background
    global shotsTakenInPeriod
    global menuSelect
    global menuSelected
    global menuSelection
    global aimRadius
    global difficultySelection
    
    # set coordnate plane for easy translation from the joystick position
    # xll, yll, xur, yur
    threading.Thread(target=scoreLoop).start()
    win.setCoords(SCREEN_WIDTH, 0, 0, SCREEN_HEIGHT)
    win.setBackground("Grey")
    backgroundImage = Image(Point((SCREEN_WIDTH / 2), SCREEN_HEIGHT / 2), background)
    backgroundImage.draw(win)
    
    dog = Image(Point(centerX,centerY), "/home/ludwigg/Python/PyRpi_DuckHunt/dog.png")
    
    # Main Menu Setup
    menuButton = []
    for i in range(3):
        innerList = []
        innerList.append(Image(Point(SCREEN_WIDTH / 2, (SCREEN_HEIGHT / 2) + (80 - i * (80))), menuSelect))
        innerList.append(Image(Point(SCREEN_WIDTH / 2, (SCREEN_HEIGHT / 2) + (80 - i * (80))), menuSelected))
        temp = Text(Point(SCREEN_WIDTH / 2, (SCREEN_HEIGHT / 2) + (80 - i * (80))), "")
        if i == 0:
            temp.setText("Play")
        elif i == 1:
            temp.setText("Settings")
        else:
            temp.setText("Quit")
        temp.setTextColor("white")
        temp.setSize(20)
        innerList.append(temp)
        menuButton.append(innerList)
        
    for items in menuButton:
        items[0].draw(win)
        items[2].draw(win)
    
    menuSelection = 0
    timeStickMoved = 0
    
    menuButton[menuSelection][0].undraw() # undraw normal button
    menuButton[menuSelection][2].undraw() # undraw text
    menuButton[menuSelection][1].draw(win) # draw selected button
    menuButton[menuSelection][2].draw(win) # draw text
    
    while not playing:
        if time.time() > timeStickMoved + .2:
            if getRawY() > .7:
                menuButton[menuSelection][1].undraw() # undraw selected
                menuButton[menuSelection][2].undraw() # undraw text
                menuButton[menuSelection][0].draw(win) # draw normal button
                menuButton[menuSelection][2].draw(win) # draw text
                menuSelection -= 1
                if menuSelection < 0:
                    menuSelection = 2
                menuButton[menuSelection][0].undraw() # undraw normal button
                menuButton[menuSelection][2].undraw() # undraw text
                menuButton[menuSelection][1].draw(win) # draw selected button
                menuButton[menuSelection][2].draw(win) # draw text
                timeStickMoved = time.time()
            elif getRawY() < .3:
                menuButton[menuSelection][1].undraw() # undraw selected
                menuButton[menuSelection][2].undraw() # undraw text
                menuButton[menuSelection][0].draw(win) # draw normal button
                menuButton[menuSelection][2].draw(win) # draw text
                menuSelection += 1
                if menuSelection > 2:
                    menuSelection = 0
                menuButton[menuSelection][0].undraw() # undraw normal button
                menuButton[menuSelection][2].undraw() # undraw text
                menuButton[menuSelection][1].draw(win) # draw selected button
                menuButton[menuSelection][2].draw(win) # draw text
                timeStickMoved = time.time()
        update(60)
        
    difficultySelection = 0
    menuButton[0][2].setText("Easy")
    menuButton[1][2].setText("Normal")
    menuButton[2][2].setText("Hard")
    # menuButton[difficultySelection][0].undraw() # undraw normal button
    # menuButton[difficultySelection][2].undraw() # undraw text
    # menuButton[difficultySelection][1].draw(win) # draw selected button
    # menuButton[difficultySelection][2].draw(win) # draw text
    
    while not diffSelected:
        if time.time() > timeStickMoved + .2:
            if getRawY() > .7:
                menuButton[difficultySelection][1].undraw() # undraw selected
                menuButton[difficultySelection][2].undraw() # undraw text
                menuButton[difficultySelection][0].draw(win) # draw normal button
                menuButton[difficultySelection][2].draw(win) # draw text
                difficultySelection -= 1
                if difficultySelection < 0:
                    difficultySelection = 2
                menuButton[difficultySelection][0].undraw() # undraw normal button
                menuButton[difficultySelection][2].undraw() # undraw text
                menuButton[difficultySelection][1].draw(win) # draw selected button
                menuButton[difficultySelection][2].draw(win) # draw text
                timeStickMoved = time.time()
            elif getRawY() < .3:
                menuButton[difficultySelection][1].undraw() # undraw selected
                menuButton[difficultySelection][2].undraw() # undraw text
                menuButton[difficultySelection][0].draw(win) # draw normal button
                menuButton[difficultySelection][2].draw(win) # draw text
                difficultySelection += 1
                if difficultySelection > 2:
                    difficultySelection = 0
                menuButton[difficultySelection][0].undraw() # undraw normal button
                menuButton[difficultySelection][2].undraw() # undraw text
                menuButton[difficultySelection][1].draw(win) # draw selected button
                menuButton[difficultySelection][2].draw(win) # draw text
                timeStickMoved = time.time()
        update(60)
        
    # remove menu
    for items in menuButton:
        for thing in items:
            try:
                thing.undraw()
            except:
                None
        
    message.setTextColor("white")
    message.setSize(20)
    message.draw(win)
    
    roundText.setTextColor("white")
    roundText.setSize(20)
    
    scoreText.setTextColor("white")
    scoreText.setSize(25)
    scoreText.draw(win)
    
    ducksMissedText.setTextColor("white")
    ducksMissedText.setSize(20)
    ducksMissedText.draw(win)
    
    shotsTakenText.setTextColor("white")
    shotsTakenText.setSize(15)
    shotsTakenText.draw(win)
    
    aim.draw(win)
    innerAim.draw(win)
    
    timeRoundStart = 0
    timeForRoundDisplay = 2 # sec
    
    SetupRound()
    timeRoundStart = time.time() + timeForRoundDisplay
    roundDrawn = False
    while(playing and not quit):
        #timeLeft = round(end - time.time(), 2)
        if ducksMissed >= 10:
            message.setText("Game Over!")
            #scoreText.setText("Final Score: " + str(totalScore))
            dog.draw(win)
            playing = False
        elif timeRoundStart - time.time()> 0:
            if not roundDrawn:
                roundText.draw(win)
                aim.undraw()
                innerAim.undraw()
                for duck in ActiveDucks:
                    duck.duckGraphic().undraw()
                roundDrawn = True
            roundText.setText("Round: " + str(roundNum))
        else:
            #message.setText(timeLeft)
            if roundDrawn:
                roundText.undraw()
                for duck in ActiveDucks:
                    duck.duckGraphic().draw(win)
                roundDrawn = False
            scoreText.setText("Score: " + clockOutput)
            ducksMissedText.setText("Ducks Missed: " + str(ducksMissed))
            shotsTakenText.setText("Shots")
            
            if RoundCheck():
                if time.time() - timeAtLastRound > TIME_BETWEEN_ROUNDS and len(unDrawDuck) == 0:
                    if roundScore == NUM_DUCKS_PER_ROUND:
                        totalScore += 10
                    SetupRound()
                    timeRoundStart = time.time() + timeForRoundDisplay
                    for duck in deadDuckDisplay:
                        duck.undraw()
            
            CanClear = True
            for i in range(shotsTakenInPeriod):
                try:
                    bullets[-(i + 1)].undraw()
                except:
                    None
                
            for unDraw in unDrawDuck:
                try:
                    #duckCenter = unDraw.duckGraphic().getAnchor()
                    if not unDraw.FlyingAway:
                        unDraw.duckGraphic().undraw()
                        if len(indexKilledDucks) > 0:
                            duckDisplay[indexKilledDucks[0]].undraw()
                            deadDuckDisplay[indexKilledDucks[0]].draw(win)
                            del indexKilledDucks[0]
                    
                    elif unDraw.duckGraphic().getAnchor().y > SCREEN_HEIGHT + 20:
                        ducksMissed += 1
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
            
            try:
                aim.undraw()
                innerAim.undraw()
            except:
                None
            
            aim = Circle(Point(getXPosition(), getYPosition()), aimRadius)
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
                    elif duckCenter.y <= 117:
                        duck.setVelocityY(abs(duck.getRawVelocityY()))
                        
                    duck.duckGraphic().move(duck.getVelocityX(), duck.getVelocityY())
            
            # if (deathTime - time.time()) < 0:
                # try:
                    # death.undraw()
                # except:
                    # print()
        
        updateScore()
        update(60)
    
    win.close()

# Setup GPIO0
GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(26, GPIO.IN)
GPIO.setup(14, GPIO.IN)

GPIO.add_event_detect(26, GPIO.FALLING, callback=shoot, bouncetime=300)
GPIO.add_event_detect(14, GPIO.FALLING, callback=reset, bouncetime=300)

segments = (GPIO_A, GPIO_B, GPIO_C, GPIO_D, GPIO_E, GPIO_F, GPIO_G)
digits = (GPIO_D1, GPIO_D2, GPIO_D3, GPIO_D4)

# sets all segments off
for segment in segments:
	GPIO.setup(segment, GPIO.OUT)
	GPIO.output(segment, 0)
	
# sets all digits to 1, aka not grounded
for digit in digits:
	GPIO.setup(digit, GPIO.OUT)
	GPIO.output(digit, 1)
	
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