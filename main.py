import generator
import evaluator
import mutator
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
    #print "Key: "+k
    obj = r.hgetall(k)
    r.hset(k, "status", "inprogress")
    return obj['string']

def iterate():
    start = time.time()
    #Generate all creatures
    for i in range(generationSize):
        generator.generate(random.randrange(15))
    #Evaluate all creatures
    for i in range(generationSize):
        key = getKey()
        robot = getRobot(key)
        #print str(i+1) + " of " + str(generationSize)
        result = evaluator.evaluate(robot)
        resultsDb.hmset(key, {"string":robot, "result":result})
        #r.hset(key, "status", "complete")
        r.delete(key)
    end = time.time()
    print(end - start)
    #Natural Selection
    results = resultsDb.keys('*')
    rankings = []
    sortedResults = {}
    for k in results:
        obj = resultsDb.hgetall(k)
        sortedResults[obj['result']] = obj['string']
        rankings.append(obj['result'])
    rankings = sorted(rankings)[generationSize/2:]
    print rankings
    nextGen = [sortedResults[rank] for rank in rankings]

    #Create next generation
    for x in nextGen:
        mutator.mutate(x)
        mutator.mutate(x)

numGenerations = 10
generationSize = 10
r = redis.Redis(host='127.0.0.1', port=6379, db=0)
resultsDb = redis.Redis(host='127.0.0.1', port=6379, db=1)
r.flushdb()
resultsDb.flushdb()
for i in range(numGenerations):
    print "Generation " + str(i+1) + " of " + str(numGenerations)
    iterate()
    r.flushdb()
    resultsDb.flushdb()
import pdb; pdb.set_trace()
