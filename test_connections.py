import pytest
from elasticsearch import Elasticsearch
import redis
import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def test_redis_conf():
    conf = load(open('conf.yml','r'), Loader=Loader)
    db = redis.Redis(host=conf['redis'], port=6379, db=0)
    try:
        assert db.ping() == True
    except redis.ConnectionError:
        pytest.fail()

def test_elastic_conf():
    conf = load(open('conf.yml', 'r'), Loader=Loader)
    es = Elasticsearch([conf['elasticsearch']])
    assert es.ping()
