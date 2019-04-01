import generator
import evaluator
import redis
import random
import time

def getKey():
    k = None
    while True:
        k = r.randomkey()
        obj = r.hgetall(k)
        if obj['status'] == 'todo':
            break
    return k

def getRobot(k):
    print "Key: "+k
    obj = r.hgetall(key)
    r.hset(key, "status", "inprogress")
    return obj['string']


start = time.time()
generationSize = 10
r = redis.Redis(host='127.0.0.1', port=6379, db=0)
resultsDb = redis.Redis(host='127.0.0.1', port=6379, db=1)
#Generate all creatures
for i in range(generationSize):
    generator.generate(random.randrange(15))

#Evaluate all creatures
import pdb; pdb.set_trace()
for i in range(generationSize):
    key = getKey()
    robot = getRobot(key)
    print str(i) + " of " + str(generationSize)
    result = evaluator.evaluate(robot)
    resultsDb.hmset(key, {"string":robot, "result":result})
    #r.hset(key, "status", "complete")
    r.delete(key)

end = time.time()

print(end - start)


#Create next generation
