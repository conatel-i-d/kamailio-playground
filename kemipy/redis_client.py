import os
import redis

from exceptions import UndefinedEnvironmentVariable

REDIS_HOST = os.environ.get('REDIS_HOST', None)
REDIS_PORT = os.environ.get('REDIS_PORT', None)
REDIS_DB = os.environ.get('REDIS_DB', None)

_client = None

def create_redis_client():
    if REDIS_HOST is None:
        raise UndefinedEnvironmentVariable("REDIS_HOST")
    if REDIS_PORT is None:
        raise UndefinedEnvironmentVariable("REDIS_PORT")
    if REDIS_DB is None:
        raise UndefinedEnvironmentVariable("REDIS_DB")
    global _client
    if _client is None:
        _client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return _client