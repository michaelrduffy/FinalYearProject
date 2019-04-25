#Generate valid creatures
import random
import redis

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

conf = load(open('conf.yml','r'), Loader=Loader)
r = redis.Redis(host=conf['redis'], port=6379, db=0)

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
        if x < 50:
            if x < 25:
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
