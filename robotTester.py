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
    p.setGravity(0,0,-2)
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

testRobot = 'F(3){2}[F{1.0 2.0}(6.0 3.0),,F[F(4.0){103}]]'
evaluate(testRobot, False)