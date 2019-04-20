import redis
import random
import re
#Take in robot
r = redis.Redis(host='192.168.0.9', port=6379, db=0)

BRANCH_TERMINATORS = ['[', ']']
PARAM_STARTS = ['(', '{']
PARAM_ENDS = [')', '}']

class gene:

    char = ''
    objParams = []
    jointParams = []
    children = None
    parent = None

    def __init__(self, char):
        self.char = char

    def setParent(self, p):
        self.parent = p

    def setObjParams(self, o):
        self.objParams = o

    def setJointParams(self, j):
        self.jointParams = j

    def objParamsToString(self):
        obj = self.objParams
        if obj == None:
            return ''
        obj = [str(p) for p in obj]
        pString = '{' + ' '.join(obj) + '}'
        return pString

    def setChildren(self, c):
        self.children = c

    def jointParamsToString(self):
        obj = self.jointParams
        if obj == None:
            return ''
        obj = [str(p) for p in obj]
        pString = '(' + ' '.join(obj) + ')'
        return pString

    def childrenToString(self):
        if self.children != None:
            return '[' + self.children + ']'
        else:
            return ''

    def toString(self):
        return self.char + self.objParamsToString() + self.jointParamsToString() + self.childrenToString()

def generateKey():
    return r.dbsize()

def checkBrackets(robot):
    numOpen = 0
    numClosed = 0
    for j, c in enumerate(robot):
        if c == '[':
            numOpen += 1
        elif c == ']':
            numClosed += 1
    if numOpen > numClosed:
        return numOpen - numClosed
    return 0

#Return robot
def split(s):
 parts = []
 bracket_level = 0
 current = []
 # trick to remove special-case of trailing chars
 for c in (s + ","):
     if c == "," and bracket_level == 0:
         parts.append("".join(current))
         current = []
     else:
         if c == "[":
             bracket_level += 1
         elif c == "]":
             bracket_level -= 1
         current.append(c)
 return parts

#Modify them
def deserialise(robot):
    robotString = robot
    g = gene('F')
    i = 0
    objParams = ''
    jointParams = ''
    children = ''
    skip = 0
    if len(robotString) > 1:
        if robotString[i+1] in PARAM_STARTS:
            endChar = PARAM_ENDS[PARAM_STARTS.index(robotString[i+1])]
            end = robotString.find(endChar, i+1)
            if endChar == '}':
                objParams = robotString[i+2:end]
                skip = end
            elif endChar == ')':
                jointParams = robotString[i+2:end]
                skip = end
            i = skip
            if(len(robotString)-1 > i+1):
                if robotString[i+1] in PARAM_STARTS:
                    endChar = PARAM_ENDS[PARAM_STARTS.index(robotString[i+1])]
                    end = robotString.find(endChar, i+1)
                    if endChar == '}':
                        objParams = robotString[i+2:end]
                        skip = end
                    elif endChar == ')':
                        jointParams = robotString[i+2:end]
                        skip = end
                    i = skip

        if len(robotString)-1 > i+1 and robotString[i+1] == '[':
            g.setChildren(robotString[i+2:-1])
    objParams = objParams.split(' ') if objParams != '' else None
    jointParams = jointParams.split(' ') if jointParams != '' else None
    g.setObjParams(objParams)
    g.setJointParams(jointParams)
    # Find params
    # Find children?
    return g

#Identify genes?
def mutate(robot):
    if robot.objParams != None:
        temp = robot.objParams
        newParams = []
        for p in temp:
            foo = float(p)
            multiplier = 1 + (random.sample([-1,1],1)[0] * random.uniform(0, 0.2))
            newParams.append(str(foo * multiplier))
        if len(temp) < 4 and random.randrange(100) > 60:
            newParams.append(random.random())
        robot.setObjParams(newParams)
    elif random.randrange(100) > 60:
        robot.setObjParams([random.uniform(0.1, 1)])
    if robot.jointParams != None:
        temp = robot.jointParams
        newParams = []
        for p in temp:
            foo = float(p)
            multiplier = 1 + (random.sample([-1,1],1)[0] * random.uniform(0, 0.2))
            newParams.append(str(foo * multiplier))
        if len(temp) < 4 and random.randrange(100) > 60:
            newParams.append(random.random())
        robot.setJointParams(newParams)
    elif random.randrange(100) > 60:
        robot.setJointParams([random.uniform(0.1, 1)])
    if robot.children != None:
        #Split children
        #Mutate Recursively
        children = []
        temp = robot.children
        children = split(temp)
        newChildren = []
        for i, child in enumerate(children):
            if child != '':
                foo = deserialise(child)
                bar = mutate(foo)
                newChildren.append(bar)
                if random.randrange(100) > 60:
                    newChildren.append(',')
            else:
                newChildren.append(',')
        robot.setChildren(''.join(newChildren))
    elif random.randrange(100) > 60:
        if random.randrange(100) > 50:
            robot.setChildren('F')
        else:
            robot.setChildren(',')
    return robot.toString()

def update(robot):
    r = deserialise(robot)
    return mutate(r)
