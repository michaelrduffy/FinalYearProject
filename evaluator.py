import xmltodict as xml
import json
import pybullet as p
import time
import pybullet_data
import math
import os
import binascii
import redis
import random
import parser
from elasticsearch import Elasticsearch

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
#Recusively find links:
# - Find previous [:
  # Go back through lstring
# - Get Id and generate link

#Programmatically find edges of blocks:
#Origin + Width/2
BRANCH_TERMINATORS = ['[', ']']
conf = load(open('conf.yml','r'), Loader=Loader)
r = redis.Redis(host=conf['redis'], port=6379, db=0)
resultsDb = redis.Redis(host=conf['redis'], port=6379, db=1)
es = Elasticsearch({'host':conf['elasticsearch']})
out = None
key = -1
obj = {}
#robot = "F[F]"

#robot = "F[F[F[F[F,,F[,,F,F]]]]]"

def getKey():
    k = None
    while True:
        k = r.randomkey()
        if k == None:
            continue
        obj = r.hgetall(k)
        if 'status' not in obj.keys():
            continue
        if obj['status'] == 'todo':
            break
    return k

def getRobot(k):
    #print "Key: "+k
    obj = r.hgetall(k)
    if len(obj.keys()) == 0:
        return 'Failed'
    else:
        r.hset(k, "status", "inprogress")
    return obj['string']

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

def calcForce(phase=0):
    val = math.sin((time.time()*phase)) * 10
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
    phases = []
    with open("robot.urdf", "r") as f:
        test = f.read()
        temp = xml.parse(test)
        if temp['robot'].has_key('joint'):

            if type(temp['robot']['joint']) == list:
                phases = [{foo['@name'] : foo['phase']} for foo in temp['robot']['joint']]
            else:
                phases = [{temp['robot']['joint']['@name'] : temp['robot']['joint']['phase']}]
    velocities = []
    jointInfo = [p.getJointInfo(boxId, foo) for foo in range(p.getNumJoints(boxId))]
    ids = [foo.keys()[0] for foo in phases]

    stepCount = 5000
    for i in range (stepCount):
        p.stepSimulation()
        f = calcForce()
        for j in range(p.getNumJoints(boxId)):
            jointPhase = 0
            for phase in phases:
                if jointInfo[j][1] == phase.keys()[0]:
                    jointPhase = float(phase.values()[0])

            f = calcForce(jointPhase)
            direction = speed if f >= 0 else  speed * -1
            p.setJointMotorControl2(boxId, j, p.VELOCITY_CONTROL, targetVelocity=direction, force=math.fabs(f))

    cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
    # result = measureDistance(cubePos)
    result = measureDistance(cubePos)
    p.resetSimulation()
    p.disconnect()

    return result

while True:
    if r.dbsize() != 0:
        key = getKey()
        if not r.exists(key):
            continue

        robot = getRobot(key)
        if robot == 'Failed':
            continue
        #print str(i+1) + " of " + str(generationSize)
        print "Evaluating " + robot
        result = evaluate(robot)
        resultsDb.hmset(key, {"string":robot, "result":result})
        #r.hset(key, "status", "complete")
        r.delete(key)
    else:
        time.sleep(5)
