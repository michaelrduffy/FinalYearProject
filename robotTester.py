import xmltodict as xml
import json
import pybullet as p
import time
import pybullet_data
import math
import os
import binascii
import random
import parser
#Recusively find links:
# - Find previous [:
  # Go back through lstring
# - Get Id and generate link

#Programmatically find edges of blocks:
#Origin + Width/2
BRANCH_TERMINATORS = ['[', ']']
out = None
key = -1
obj = {}

#Read string char by char
#Could turn into a list comprehension

#Lists of lists
# New List on [], filled with children
# Is this bad? - Probably
cubeStartPos = [0,0,0]

def generate_id():
    return binascii.b2a_hex(os.urandom(4))

# x = [translate_char(char, i) for i, char in enumerate(robot) if char not in ['[',']']]

def calcForceCos():
    val = math.cos((time.time())) * 10
    return val

def calcForce():
    val = math.sin((time.time())) * 10
    return val

def measureDistance(pos):
    sum = 0
    for i in range(len(pos)):
        sum += (math.fabs(pos[i] - cubeStartPos[i]))**2
    return math.sqrt(sum)


def avgSpeed(v):
    if len(v) == 0:
        return 0
    #Sample velocities approx 10%
    size = int(len(v) * 0.05)
    count = int(len(v) - 1 )
    sample = [ v[random.randrange(count)] for x in range(size)]
    speeds = [math.sqrt(f[0]**2 + f[1]**2 + f[2]**2) for f in sample]
    x = 0.0
    y = 0.0
    z = 0.0
    for vel in sample:
        x += vel[0]
        y += vel[1]
        z += vel[2]
    count = float(len(v))
    x = x / count
    y = y / count
    z = z / count

    mean = math.sqrt(x**2 + y**2 + z**2)
    median = speeds[int(len(speeds)/2)]
    #Median Speed
    diff = 1 / math.fabs(mean - median)
    return diff


def evaluate(inputStr, headless=True):
    name = parser.build_robot(inputStr)
    speed = 10
    physicsClient = None
    if headless:
        physicsClient = p.connect(p.DIRECT)
    else:
        physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version
    p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
    p.setGravity(0,0,-10)
    planeId = None
    try:
        planeId = p.loadURDF("plane.urdf")
    except:
        print "Plane Failed"
    cubeStartPos = [0,0,0]
    cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
    boxId = None
    boxId = p.loadURDF(name,cubeStartPos, cubeStartOrientation)
    velocities = []
    stepCount = 30000
    for i in range (stepCount):
        p.stepSimulation()
        f = calcForce()
        for j in range(p.getNumJoints(boxId)):
            if j % 2 == 0:
                f = calcForce()
            else:
                f = calcForceCos()
            direction = speed if f >= 0 else  speed * -1
            v = p.getBaseVelocity(boxId)[0]
            velocities.append(v)
            p.setJointMotorControl2(boxId, j, p.VELOCITY_CONTROL, targetVelocity=direction, force=math.fabs(f))


    cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
    # result = measureDistance(cubePos)
    result = measureDistance(cubePos)
    p.resetSimulation()
    p.disconnect()

    return result

testRobot = 'F{0.0726458923378 0.0600170558428 0.314057799853 0.411015160035}(0.341207171124 0.499099023995 0.738599451703 3.13755017146)[F{0.820816651506 0.278738621582 73.458478249 0.272362756109}(0.231917878423 0.420992724841 0.275109006267 0.414710442446)[,,F{0.0571422971879 0.096995791126 0.49890453027 0.084657221213}(0.0652296257035 0.0687225718365 0.127551461775 2.16932125434)[,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,],,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,],,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]'
evaluate(testRobot, False)
