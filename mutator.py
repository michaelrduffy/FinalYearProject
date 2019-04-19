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

#Modify them
def deserialise(robot):
    robotString = robot
    g = gene('F')
    i = 0
    objParams = ''
    jointParams = ''
    children = ''
    skip = 0
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
    if robotString[i+1] == '[':
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
        print 'Has objParams'
        #Mutations Here
    if robot.jointParams != None:
        print 'Has jointParams'
        #Mutations Here
    if robot.children != None:
        #Split children
        #Mutate Recursively
        print 'children: ' + robot.childre

        temp = deserialise(robot.children)
        ch = robot.children[len(temp.toString()):]
        
    return robot.toString()

#Return robot

testStr = 'F{6.0 3.2}(1.0)[F{0.1 0.0}(1.1)[F[F]],F[F{0.1}(1 2 3),,,F]]'
genome = deserialise(testStr)
mutate(genome)

# def mutate(robot):
#     # for i, char in enumerate(robot):
#     #     if char == ',':
#     #         if random.randrange(100) > 80:
#     #             if random.randrange(100) > 95:
#     #                 robot = robot[:i] + 'F' + robot[i+1:]
#     #             else:
#     #                 robot = robot[:i] + ',' + robot[i+1:]
#     #
#     #     if char == 'F' and i > 0:
#     #         if random.randrange(100) > 90 and robot[i+1] != '[' :
#     #             robot = robot[:i] + "F[]" + robot[i+1:]
#     # for i in range(checkBrackets(robot)):
#     #     robot += ']'
#     subString = robot
#     str_iter = enumerate(subString)
#     newStr = ''
#     for i, char in str_iter:
#         if char not in BRANCH_TERMINATORS and char in ['F']:
#             print char
#             if char == ',':
#                 if random.randrange(100) > 80:
#                     subString[i] = "F"
#                 continue
#             objParams = ''
#             jointParams = ''
#             skip = 0
#             if subString[i+1] in PARAM_STARTS:
#                 endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
#                 end = subString.find(endChar, i+1)
#                 if endChar == '}':
#                     objParams = subString[i+2:end]
#                     skip = end
#                 elif endChar == ')':
#                     jointParams = subString[i+2:end]
#                     skip = end
#                 i = i+skip
#                 if(len(subString)-1 > i+1):
#                     if subString[i+1] in PARAM_STARTS:
#                         endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
#                         end = subString.find(endChar, i+1)
#                         if endChar == '}':
#                             objParams = subString[i+2:end]
#                             skip = end
#                         elif endChar == ')':
#                             jointParams = subString[i+2:end]
#                             skip = end
#                         i = i+skip
#
#             # elif random.randrange(100) > 80:
#             #     if random.randrange(100) > 90:
#             #         subString = subString[:i] + "(0.0)" + subString[i+1:]
#             #         skip = skip + 2
#             #     else:
#             #         subString = subString[:i] + "{0.0}" + subString[i+1:]
#             #         skip = skip + 2
#             objParams = objParams.split(' ') if objParams != '' else None
#             jointParams = jointParams.split(' ') if jointParams != '' else None
#             newGene = gene(char, objParams, jointParams)
#             import pdb; pdb.set_trace()
#             print newGene.toString()
#             # if objParams != None and i != 0:
#             #     for idx, p in enumerate(objParams):
#             #         if p != '':
#             #             if random.randrange(100) > 70:
#             #                 mod = random.sample([-1,1], 1)[0] * (1.0 + random.uniform(-0.2, 0.2))
#             #                 p = float(p) * mod
#             #     if len(objParams) < 4:
#             #         pString = ''
#             #         objParams.append(0.0)
#             #         objParams = [str(p) for p in objParams]
#             #         pString = '{' + ' '.join(objParams) + '}'
#             #
#             #         subString = subString[:i-skip+1] + pString + subString[i-1:]
#             # import pdb; pdb.set_trace()
#             # if jointParams != None and i != 0:
#             #     for idx, p in enumerate(jointParams):
#             #         if p != '':
#             #             if random.randrange(100) > 70:
#             #                 mod = random.sample([-1,1], 1)[0] * (1.0 + random.uniform(-0.2, 0.2))
#             #                 p = float(p) * mod
#             #     if len(jointParams) < 5:
#             #         pString = ''
#             #         jointParams.append(0.0)
#             #         jointParams = [str(p) for p in jointParams]
#             #         pString = '(' + ' '.join(jointParams) + ')'
#             #
#             #         subString = subString[:i-skip+1] + pString + subString[i-1:]
#             # for foo in range(skip):
#             #     try:
#             #         str_iter.next()
#             #     except StopIteration:
#             #         continue
#     print subString
#     robotDict = {"string": subString, "status":"todo"}
#     # r.hmset(generateKey(), robotDict)
#     return robot
