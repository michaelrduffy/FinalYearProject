import pytest
from elasticsearch import Elasticsearch
import redis
import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

@pytest.mark.parametrize("redisHost,expected", [("192.168.256.9", True), ("127.0.0.1", True)])
def test_redis_connection(redisHost, expected):
    db = redis.Redis(host=redisHost, port=6379, db=0)
    result = ''
    try:
        db.client_id()
    except redis.ConnectionError:
        result = True
    finally:
        assert result == expected

def test_redis_conf():
    conf = load(open('conf.yml','r'), Loader=Loader)
    db = redis.Redis(host=conf['redis'], port=6379, db=0)
    try:
        db.client_id()
    except redis.ConnectionError:
        pytest.fail("No Connection to Redis")

def test_elastic_conf():
    conf = load(open('conf.yml', 'r'), Loader=Loader)
    es = Elasticsearch({'host':conf['elasticsearch']})
