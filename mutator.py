import redis
import random
#Take in robot
r = redis.Redis(host='192.168.0.9', port=6379, db=0)

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
    for i, char in enumerate(robot):
        if char == ',':
            if random.randrange(100) > 80:
                if random.randrange(100) > 95:
                    robot = robot[:i] + 'F' + robot[i+1:]
                else:
                    robot = robot[:i] + ',' + robot[i+1:]

        if char == 'F' and i > 0:
            if random.randrange(100) > 90 and robot[i+1] != '[' :
                robot = robot[:i] + "F[]" + robot[i+1:]
    for i in range(checkBrackets(robot)):
        robot += ']'
    robotDict = {"string": robot, "status":"todo"}
    r.hmset(generateKey(), robotDict)
    return robot

#Identify genes?

#Modify them

#Return robot
