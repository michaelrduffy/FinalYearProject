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

testRobot = 'F{0.939525557487 0.108968548488 0.591570418595 0.139907521559}(0.0534390729531 0.0782987271143 0.702292718791 0.123099732771)[F{0.921678685891 2.46947253767 14.9986553647 0.00941316382342}(0.301625128562 0.617852250251 0.422979897998 0.218339761083)[F{0.735301547431 0.177767662442 0.628658119032 0.291319160948}(0.176960161023 1.55660796486 0.518319257775 0.630823991482)[F{0.407954506895 0.0260614217489 0.833297365098 0.22388474015}(0.889844884604 0.110634755554 0.390303287892 0.936662401522)[F{0.0951679645192 0.287083765451 0.381885222746 0.204045636959}(0.0985078450131 0.211011172414 0.18639775257 3.02010544982)[F{0.126385484072 0.0294243630618 0.441269255416 0.410843025168}(0.0481166761282 0.136045390951 0.80844262931 0.430506253677)[F{0.155911083713 1.99489364637 2.06897206694 0.472578400556}(0.276936214224 0.118741394154 0.164825052973 0.287839467992)[F{0.435746365216 0.363298025834 0.752716734826 0.44457060806}(0.123990190791 0.0214681764412 0.840410798026 0.344303572911)[F{0.732408760143 0.267720171699 0.0514443268262 0.155114581968}(0.784508887524 1.569849999 0.0160532656442 0.214649296087)[F{0.899582718725 0.178117103996 1.52920168617 0.190012381774}(1.46271123232 1.27091622642 0.954950862974 2.20084267253)[F{0.914059720555 0.00295259561797 0.934537002255 0.104243154945}(0.532608561977 0.198345354949 0.0197720447225 2.00438893527)[F{0.88345487996 0.162856812167 0.0425005109038 0.328971508924}(1.22916396302 0.0852791048144 0.127940170571 0.138637523982)[F{0.0957677706282 0.382207069013 0.552690427898 0.0852431953487}(0.337517756167 0.998238597292 0.853994219571 0.359907729024)[F{0.343261961132 0.65633605859 0.507183770786 0.56495246382}(0.0882932177793 0.411645998321 1.95477138965 0.127936147539)[F{0.216598883484 0.948251554091 0.008562785887 0.194226209311}(1.07493291736 0.0613171268647 0.913405178648 0.908442250226)[F{0.116934075726 0.315452966126 0.209178753545 3.47215063059}(0.56750588614 0.347943308952 0.360242246413 0.90129900073)[F{0.451314649416 1.19773593084 0.661053123485 0.704435814575}(0.887619921944 0.184273294214 0.242415968747 0.0274274756374)[F{0.45261578485 0.00362612130999 0.252362806295 0.697232223158}(0.342176155731 0.586434170374 1.36419272373 0.766729080531)[F{1.0556545576 0.0593178399509 0.617076152232 1.01471227814}(0.685658642747 0.346771752825 0.202795705624 0.367390412218)[F{0.210066279009 0.289277189496 0.969470430808 0.385038327795}(0.632382287653 0.161697539646 0.00205801021975 0.532970011488)[F{0.294730131867 0.533085522827 0.404086416388 0.106080324754}(0.286944413211 1.06013662107 0.0476804152528 0.30986198533)[F{0.259245994655 0.249514966933 0.849783048494 0.38871675916}(0.484497540962 0.546555776086 0.167919092896 0.761329870097)[F{0.114532800514 0.446022318063 0.426835817314 0.419529990161}(1.01273300723 1.26965090576 0.385481789154 0.186456282538)[F{0.157406016763 0.0160190756953 0.284349672917 1.34629031671}(0.362261196927 0.617816385529 0.204402536017 0.713677545815)[F{0.759235702041 0.585733314727 0.301355117032 0.743590971744}(0.452043773743 0.0170276441487 0.779675676927 0.310017857298)[F{0.530798675507 0.53550342431 0.0505440062177 0.222117140282}(0.739105529491 0.970497010646 0.653156246441)[F{0.585306122813 0.92835798434 0.854936981938 0.732070431374}(0.379549072891 0.398570498535)[F{0.122304653051 0.662419708154 0.389865746663}(0.550881603857 0.681594632983 0.0625635820167 0.743976160895)[F{0.694101922883 0.0761047270618 0.769762001668}(0.273341815603 0.413791371042 0.38347768472 0.763753028735)[F{0.201644605174 0.124126929724}(0.400718099865 0.419545592366)[F{0.441079627731 0.933535687198 0.468313010986}(0.204132595834 0.517994538404 0.585021636223 0.495816321121)[F(0.409229658319)[F]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]'
evaluate(testRobot, False)
