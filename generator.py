#Generate valid creatures
import random
import redis

r = redis.Redis(host='192.168.0.9', port=6379, db=0)

def findNextBracket(robot, start):
    return robot.find("[", start+1, len(robot))

def generateKey():
    return r.dbsize()

def generate(n=10):
    robot = "F[]"
    numLayers = n
    startPos = 1
    for i in range(numLayers):
        x = random.randrange(100)
        if x > 25:
            if x > 50:
                robot = robot[:startPos+1] + "F[]" + robot[startPos+1:]
                startPos += 2
            else:
                robot = robot[:startPos+1] + "F" + robot[startPos+1:]
                startPos += 1
        else:
            robot = robot[:startPos+1] + "," + robot[startPos+1:]
            startPos += 1
    robotDict = {"string": robot, "status":"todo"}
    r.hmset(generateKey(), robotDict)
    return robot
