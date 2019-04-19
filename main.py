import generator
import mutator
import redis
import random
import time
import string

from datetime import datetime
from elasticsearch import Elasticsearch

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

def runId():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

def iterate(gen, Id):
    start = time.time()
    #Generate all creatures
    if gen == 0:
        for i in range(generationSize):
            generator.generate(random.randrange(10))
    #Evaluate all creatures
    #Wait for evaluations
    if len(r.keys()) != generationSize:
        import pdb; pdb.set_trace()
    while len(r.keys()) != 0:
        time.sleep(5)
        print "Waiting for evaluation to finish"
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
        doc = obj.copy()
        doc['generation'] = gen
        doc['runId'] = Id
        res = es.index(index='creature_index_test', doc_type='_doc', body=doc)
    split = generationSize/2 if generationSize % 2 == 0 else (generationSize + 1)/2
    rankings = sorted(rankings)[split:]
    print rankings
    nextGen = [sortedResults[rank] for rank in rankings]
    #Create next generation
    if gen != numGenerations-1:
        for x in nextGen:
            mutator.mutate(x)
            mutator.mutate(x)

numGenerations = 10000
generationSize = 100
es = Elasticsearch(['192.168.0.9'])
runId = runId()
r = redis.Redis(host='192.168.0.9', port=6379, db=0)
resultsDb = redis.Redis(host='192.168.0.9', port=6379, db=1)
print "RunId: " +runId
r.flushdb()
resultsDb.flushdb()
for i in range(numGenerations):
    print "Generation " + str(i+1) + " of " + str(numGenerations)
    iterate(i, runId)
    print "RunId: " +runId
    resultsDb.flushdb()
