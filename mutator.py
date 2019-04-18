import redis
import random
#Take in robot
r = redis.Redis(host='192.168.1.16', port=6379, db=0)

BRANCH_TERMINATORS = ['[', ']']
PARAM_STARTS = ['(', '{']
PARAM_ENDS = [')', '}']

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

def mutate(robot):
    # for i, char in enumerate(robot):
    #     if char == ',':
    #         if random.randrange(100) > 80:
    #             if random.randrange(100) > 95:
    #                 robot = robot[:i] + 'F' + robot[i+1:]
    #             else:
    #                 robot = robot[:i] + ',' + robot[i+1:]
    #
    #     if char == 'F' and i > 0:
    #         if random.randrange(100) > 90 and robot[i+1] != '[' :
    #             robot = robot[:i] + "F[]" + robot[i+1:]
    # for i in range(checkBrackets(robot)):
    #     robot += ']'
    subString = robot
    str_iter = enumerate(subString)
    newStr = ''
    for i, char in str_iter:
        if char not in BRANCH_TERMINATORS:
            if char == ',':
                if random.randrange(100) > 80:
                    subString[i] = "F"
                continue
            objParams = ''
            jointParams = ''
            skip = 0
            if subString[i+1] in PARAM_STARTS:
                endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
                end = subString.find(endChar, i+1)
                if endChar == '}':
                    objParams = subString[i+2:end]
                    skip = end
                elif endChar == ')':
                    jointParams = subString[i+2:end]
                    skip = end
                i = i+skip
                if(len(subString)-1 > i+1):
                    if subString[i+1] in PARAM_STARTS:
                        endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
                        end = subString.find(endChar, i+1)
                        if endChar == '}':
                            objParams = subString[i+2:end]
                            skip = end
                        elif endChar == ')':
                            jointParams = subString[i+2:end]
                            skip = end
                        i = i+skip
            elif random.randrange(100) > 80:
                if random.randrange(100) > 90:
                    subString = subString[:i] + "(0.0)" + subString[i+1:]
                    skip = skip + 2
                else:
                    subString = subString[:i] + "{0.0}" + subString[i+1:]
                    skip = skip + 2
            objParams = objParams.split(' ') if objParams != '' else None
            jointParams = jointParams.split(' ') if jointParams != '' else None
            if objParams != None and i != 0:
                for idx, p in enumerate(objParams):
                    if p != '':
                        if random.randrange(100) > 70:
                            mod = random.sample([-1,1], 1)[0] * (1.0 + random.uniform(-0.2, 0.2))
                            p = float(p) * mod
                if len(objParams) < 4:
                    objParams.append(0.0)
                    objParams = [str(p) for p in objParams]
                    pString = '{' + ' '.join(objParams) + '}'
                    subString[:i-skip+1] + pString + subString[i:]
            if jointParams != None and i != 0:
                for idx, p in enumerate(jointParams):
                    if p != '':
                        if random.randrange(100) > 70:
                            mod = random.sample([-1,1], 1)[0] * (1.0 + random.uniform(-0.2, 0.2))
                            p = float(p) * mod
                if len(jointParams) < 5:
                    jointParams.append(0.0)
                    jointParams = [str(p) for p in jointParams]
                    pString = '(' + ' '.join(jointParams) + ')'
                    subString[:i-skip+1] + pString + subString[i:]
            newStr = newStr + char
            print subString
            for foo in range(skip):
                try:
                    str_iter.next()
                except StopIteration:
                    continue
    print subString
    robotDict = {"string": subString, "status":"todo"}
    # r.hmset(generateKey(), robotDict)
    return robot

#Identify genes?

#Modify them

#Return robot

testStr = 'F[F{0.1 0.0}]'
mutate(testStr)
