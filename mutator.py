import redis
import random
#Take in robot
r = redis.Redis(host='192.168.0.9', port=6379, db=0)

def generateKey():
    return r.dbsize()

def mutate(robot):
    for i, char in enumerate(robot):
        if char == ',':
            if random.randrange(100) > 50:
                robot = robot[:i] + robot[i+1:]
        if char == 'F' and i > 0:
            if random.randrange(100) > 50:
                robot = robot[:i] + "F[]" + robot[i+1:]
    robotDict = {"string": robot, "status":"todo"}
    r.hmset(generateKey(), robotDict)
    return robot

#Identify genes?

#Modify them

#Return robot
