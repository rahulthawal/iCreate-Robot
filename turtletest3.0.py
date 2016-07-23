import create #create calls serial
import sense
import time
import msvcrt
import turtle

totalBumps = 0 #used to play Mario song once we've first found a wall - not used for anything else yet.
SWF = False #Straight Wall Found - same concept as angle set
BeginMapping = False #start of mapping algorithms
mapAngle = 0 #angle sent to map
lastStraightWall = 0 #last confirmed straight wall
robotHeading = 0 #direction robot is head similar to compass
compass = 'X' #used to track N,S,E,W
compassHistory = [compass] #array to track history of discovered walls.
wallDistance = 0 #used to track how long we have been trying to follow a straight wall

#initialize sensor readings
wall = 0
angle = 0
bumpLeft = 0
bumpRight = 0
distance = 0
wallFound = 0

songMario = [(76, 12),
            (76, 12),
            (20, 12),
            (76, 12),
            (20, 12),
            (72, 12),
            (76, 12),
            (20, 12),
            (79, 12),
            (20, 36),
            (67, 12),
            (20, 36)
            ]

songCharge = [(60, 8),
	(65, 8),
	(69, 8),
	(72, 16),
	(69, 8),
	(72, 16)
            ]

songZelda = [(65, 8),
		(70, 8),
		(70, 8),
		(72, 8),
		(74, 8),
		(75, 8),
		(77, 32)
             ]

#makes the robot status history array
history = []

status = 'SW' #Searching for Wall
for i in range(9):#initializes robot status array
    history.append(status)
    
tm = time.time() #time of starting code


#maintains angle in 0-360 range  e.g. -10 = 350, 370 = 10
def robotHeadingFixRange():
    global robotHeading
    if (robotHeading < 0):
        robotHeading += 360
    elif (robotHeading > 360):
        robotHeading -= 360


r = create.Create('COM4') #sets up robot com port
r.toFullMode()  #safe mode is annoying
r.setLEDs(0, 255, 1, 1) #sets all LEDs on
#r.demo(3) #follow wall demo - internal program to the robot

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxturn this back on 
r.playSong(songCharge)
time.sleep(1)  #Plays charge song before moving.

turtle.setup(1000, 1000, 0, 0)#initializes Turtle map 1000x1000 & starting point is center x center

while True:    #robot moving loop
#sensor readings
    #if (msvcrt.kbhit()):  #allows us to break out of code using ctrl-c for debugging (not available in idle)
    #    break
    
    #sensor input
    angle = r.getSensor("ANGLE") #angle since last measurement was taken
    #casterDrop = r.getSensor("BUMPS_AND_WHEEL_DROPS")[0]
    #leftWheelDrop = r.getSensor("BUMPS_AND_WHEEL_DROPS")[1]
    #rightWheelDrop = r.getSensor("BUMPS_AND_WHEEL_DROPS")[2]
    bumpLeft = r.getSensor("BUMPS_AND_WHEEL_DROPS")[3]
    bumpRight = r.getSensor("BUMPS_AND_WHEEL_DROPS")[4]
    #cliffLeft = r.getSensor("CLIFF_LEFT_SIGNAL")
    #cliffFrontLeft = r.getSensor("CLIFF_FRONT_LEFT_SIGNAL")
    #cliffFrontRight = r.getSensor("CLIFF_FRONT_RIGHT_SIGNAL")
    #cliffRight = r.getSensor("CLIFF_RIGHT_SIGNAL")
    distance = r.getSensor("DISTANCE") #distance since last distance was taken    
    wall = r.getSensor("WALL_SIGNAL")

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxturn this back on 
The Journey Begins
    if (totalBumps == 1):  #if we've bumped into a wall for the very first time
        r.playSong(songMario)
        totalBumps = 2  #only play Mario song once

#wall follow algorithm    
    if (bumpRight == 0 and bumpLeft == 0):  #if none of the bumper have hit.
        #follow wall control loop
        #currently only based on position control P
        #could be made better by utilizing position/integral control PI, or even better using position/integral/differential control PID.
        if (wallFound == 1): #needs to see wall first & then implemants follow wall
            if (wall > 20): #wall is too close
                r.go(20, 10) #arc left CCW
                #print ('Wall Close', wall)  #for trouble shooting & sensor calibration
                status = 'WC'
            elif (wall < 10 and wall != 0): #wall is too far
                r.go(20, -10) #arc right CW
                #print ('Wall Far', wall)   #for trouble shooting & sensor calibration
                status = 'WF'
            elif (wall == 0):
                #r.go(0)#get rid of
                time.sleep(.2) #go past where is sensed the wall gone... XXX waited an amount of time before turning quickly, we can handle this better.
                ##maybe add in additional time delay if we were straight following a wall for a while
                r.go(20, -100) #arc to the right CW
                #print ('Wall Gone', wall)  #for trouble shooting & sensor calibration
                status = 'WG'
                #printSDist() #calculates distance then prints to map
                ##XXXXXXXXXXXXXXXXXXXXXX WE NEED TO MAKE THIS PART SMARTER, MAYBE INCLUDE A WHILE LOOP BASED ON DISTANCE OR TIME TO HELP IT GO AROUND CORNER XXXX
            else:
                r.go(20) #Straight follow of wall
                #print ('Going Straight', wall)  #for trouble shooting & sensor calibration
                status = 'WS'

        else:
            r.go(20)#go straight at start of program if wall has never been found.
        

#Both hit
    elif (bumpRight == 1 and bumpLeft == 1): #need to tune this for finding a left turn corner
        r.go(-20) #goes backwards
        time.sleep(.1) #for a .1 seconds
        r.go(0, 50) #turn left (LEFT IS Positive)
        time.sleep(1) #for a .2 seconds
        wallFound = 1 #triggers that a wall has been found initially (only used once to enter wall found loop)
        #print ('Both Bumps') #for debugging purposes
        totalBumps += 1 #for playing Mario song only
        status = 'BC'
       
#Right Bumper Hits
    elif (bumpRight == 1 and bumpLeft == 0): #works to align robot to wall if only right bumper hits
        r.go(0, 50) #turn left (LEFT IS Positive)
        time.sleep(.2) #for a .2 seconds
        wallFound = 1 #triggers that a wall has been found initially (only used once to enter wall found loop)
        #print ('Right Bumps') #for debugging purposes
        totalBumps += 1 #for playing Mario song only
        status = 'BR'

#Left Bumper Hits
    elif (bumpRight == 0 and bumpLeft == 1):  #Need to tune this for obstacle avoidance
        r.go(-20) #goes backwards
        time.sleep(.1)
        r.go(0, 50)#turn left CW
        time.sleep(1)  #r.waitTime(20)#for 2 sec
        r.go()#stop
        wallFound = 1 #triggers that a wall has been found initially (only used once to enter wall found loop)
        #print ('Left Bumps') #for debugging purposes
        totalBumps += 1 #for playing Mario song only
        status = 'BL'


#Robot Travel History - last 9 recorded states: WS, WG, WC, WF, BL, BR, BB, SW
    for i in range(9):
        history[i] = history[i+1]
    history[9] = status 
    #print (status) #for debugging purposes
    
    straightCount = 0 #counts the number of times in the last 9 sensor readings a optimal distance from the wall was recorded
    for i in range(9):
        if (history[i] == 'WS') or (history[i] == 'WC') or (history[i] == 'WF'): #if wall sensor has a reading & no bumps
            straightCount +=1

    if straightCount == 9:  #past 9 steps have been following a wall - no bumps & no wall gones
        SWF = True #we are pretty confident to be on a straight wall
        BeginMapping = True #since a straight portion of a wall is confirmed we will start mapping here.  XXX or maybe on a bump... idk yet...  doesnt matter right now
    else:
        SWF = False #not so confident

#Mapping algorithms
    if BeginMapping == True:
        if (SWF == True and status[0] != 'B'):  #if were following a straight wall
            #corrects angle to keep all straight walls perpendicular, since we start mapping on a straight wall (@angle 0 being the first wall found (E), math is simplified)
            if (robotHeading >= 45 and robotHeading < 135):
                mapAngle = 90 - robotHeading
                compass = 'N'
            elif (robotHeading >= 135 and robotHeading < 225):
                mapAngle = 180 - robotHeading
                compass = 'W'
            elif (robotHeading >= 225 and robotHeading < 315):
                mapAngle = 270 - robotHeading
                compass = 'S'
            elif (robotHeading >= 315 or robotHeading  < 45):
                mapAngle = 0 - robotHeading
                compass = 'E'
            else:
                mapAngle = 0#corrects for slight error in robot angle sensors while going straight 
            if (compassHistory[len(compassHistory)-1] != compass):
                compassHistory.append(compass) #tracks which directions we have found straight walls in. (straight walls are normally found after 2ft.
                wallDistance = 0 #resets wall distance
        else: #if were not followings a straight wall or we just hit a bump revert to standard angle tracking
            mapAngle = angle
            
        robotHeading = robotHeading + mapAngle #handles which direction robot is traveling at all times
        robotHeadingFixRange()        #correct robot heading to be 0-360 range
        
        turtle.left(mapAngle)    
        turtle.forward(distance/100)
        
        wallDistance = wallDistance + distance #tracks distance that we have been following wall (also includes non straight obstacles)
        #print (compassHistory, wallDistance)   #diagnostics
        
    #print(time.time()-tm)
    #print(straightCount)
    if ((status[0] == 'B') and (compassHistory[len(compassHistory)-2] == 'N') and (compassHistory[len(compassHistory)-1] == 'E') and (wallDistance > 12000)):
        break  #breaks after a bump at certain distance traveling east after a north wall
    if ((status[0] == 'B') and (time.time() - tm) >= 300):
        break  #breaks after total run time & bump

#while loop aborted upon pressing crtl-c
r.go(0)
r.playSong(songZelda)
print ('STOPPED')
time.sleep(1)
