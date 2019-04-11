import xmltodict as xml
import json
import pybullet as p
import time
import pybullet_data
import math
import os
import binascii
import redis
from elasticsearch import Elasticsearch
#Recusively find links:
# - Find previous [:
  # Go back through lstring
# - Get Id and generate link

#Programmatically find edges of blocks:
#Origin + Width/2
BRANCH_TERMINATORS = ['[', ']']
r = redis.Redis(host='192.168.0.9', port=6379, db=0)
resultsDb = redis.Redis(host='192.168.0.9', port=6379, db=1)
es = Elasticsearch({'host':'192.168.0.9'})
out = None
key = -1
obj = {}
#robot = "F[F]"

#robot = "F[F[F[F[F,,F[,,F,F]]]]]"

def getKey():
    k = None
    while True:
        k = r.randomkey()
        obj = r.hgetall(k)
        if obj['status'] == 'todo':
            break
    return k

def getRobot(k):
    #print "Key: "+k
    obj = r.hgetall(k)
    r.hset(k, "status", "inprogress")
    return obj['string']

def translate_char(char, idx):
    cube = json.loads("""
          {
            "@name": "unset",
            "visual": {
              "geometry": {
                "box": {
                  "@size": "0.2 0.2 0.2"
                }
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0.0 0"
              },
              "material": {
                "@name": "white",
                "color": {
                  "@rgba": "1 1.0 1.0 1.0"
                }
              }
            },
            "collision": {
              "geometry": {
                "box": {
                  "@size": "0.2 0.2 0.2"
                }
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0.0 0.0"
              }
            },
            "inertial": {
              "mass": {
                "@value": "1"
              },
              "inertia": {
                "@ixx": "0.000",
                "@ixy": "0.0",
                "@ixz": "0.0",
                "@iyy": "0.000",
                "@iyz": "0.0",
                "@izz": "0.0"
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0 0"
              }
            }
          }
    """)
    if char == 'F':
        temp = cube.copy()
        temp["@name"] = idx
        return temp
    elif char == '[':
        #Recursion!!?
        return 'Branch Start'
    elif char == ']':
        #End Recursion!!
        return 'Branch End'

def make_joint(parent, child, num=0):
    if num > 0:
        num = 5%num
    joint = json.loads("""
      {
            "@name": "base_flap",
            "@type": "revolute",
            "parent": {
              "@link": ""
            },
            "child": {
              "@link": ""
            },
            "axis": {
              "@xyz": "0 0 1"
            },
            "limit": {
              "@upper": "1.9",
              "@lower": "-1.9",
              "@effort": "0",
              "@velocity": "0"
            },
            "origin": {
              "@rpy": "0 0 0",
              "@xyz": "0.1 0.0 0.0"
            }
          }
    """)
    temp = joint.copy()
    temp["@name"] = parent+child
    temp["type"] = 'revolute'
    temp["parent"]["@link"] = parent
    temp["child"]["@link"] = child
    if num == 0:
        origin = "0 0.2 0"
    elif num == 1:
        origin = "0.2 0 0"
    elif num == 2:
        origin = "0 -0.2 0"
    elif num == 3:
        origin = "-0.2 0 0"
    elif num == 4:
        origin = "0 0 0.2"
        #temp["axis"] = "0 1 0"
    elif num == 5:
        origin = "0 0 -0.2"
        #temp["axis"] = "0 1 0"
    temp["origin"]["@xyz"] = origin

    return temp

#Read string char by char
#Could turn into a list comprehension

#Lists of lists
# New List on [], filled with children
# Is this bad? - Probably
cubeStartPos = [0,0,0]

def generate_id():
    return binascii.b2a_hex(os.urandom(4))

def build_robot(lstring):
    joints = []
    links = []
    def create_branch(subString, parentId):
        branch = []
        tempString = subString[:]
        childId = None
        for i, char in enumerate(subString):
            if char not in BRANCH_TERMINATORS:
                if char == ',':
                    continue
                childId = generate_id()
                temp = translate_char(char, childId)
                branch.append(temp)
                if parentId != None:
                    joints.append(make_joint(parentId, childId, i))
                if parentId == None:
                    parentId = childId
            elif char == '[':
                numOpen = 0
                numClosed = 0
                end = None
                for j, c in enumerate(tempString[i:]):
                    if c == '[':
                        numOpen += 1
                    elif c == ']':
                        numClosed += 1

                    if numOpen == numClosed and numOpen != 0:
                        end = j
                        break
                #Send parent Id
                create_branch(tempString[i+1:end+i],branch[-1]["@name"])
                break
            elif char == ']':
                #end branch
                links.extend(branch)
                return branch
        links.extend(branch)
        return branch

    branch = create_branch(lstring, None)
    return {'branch' : branch, 'joints' : joints, 'links' : links}
    '''
        Iterate through list
        on [ create new list recurse until ]
    '''

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

def evaluate(inputStr, headless=True):
    robot = inputStr
    x = build_robot(robot)
    joints = x['joints']
    links = x['links']
    out = { "robot" : {
        "@name" : "paul",
        "link" : links,
        "joint" : joints
    }}

    parents = [x['parent']['@link'] for x in joints]
    children = [x['child']['@link'] for x in joints]
    os.remove("parserTest.urdf")

    with open("parserTest.urdf", "w") as f:
        f.write(xml.unparse(out))

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
        import pdb; pdb.set_trace()
    cubeStartPos = [0,0,0]
    cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
    boxId = None
    try:
        boxId = p.loadURDF("parserTest.urdf",cubeStartPos, cubeStartOrientation)
    except:
        import pdb; pdb.set_trace()
    cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
    for i in range (1000):
        p.stepSimulation()
        f = calcForce()
        for j in range(p.getNumJoints(boxId)):
            if j % 2 == 0:
                f = calcForce()
            else:
                f = calcForceCos()
            direction = speed if f >= 0 else  speed * -1
            p.setJointMotorControl2(boxId, j, p.VELOCITY_CONTROL, targetVelocity=direction, force=math.fabs(f))

    cubePos, cubeOrn = p.getBasePositionAndOrientation(boxId)
    result = measureDistance(cubePos)
    p.resetSimulation()
    p.disconnect()
    return result

while True:
    if r.dbsize() != 0:
        key = getKey()
        robot = getRobot(key)
        #print str(i+1) + " of " + str(generationSize)
        print "Evaluating " + robot + "..."
        try:
            result = evaluate(robot)
        except:
            import pdb; pdb.set_trace()
        resultsDb.hmset(key, {"string":robot, "result":result})
        #r.hset(key, "status", "complete")
        r.delete(key)
