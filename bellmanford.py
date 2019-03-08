import redis
import time
import traceback
import datetime

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance

def Generatebellmanford():
    print("Begin table construction")
    keys = redis.keys('*')
    table = []
    i = 0
    for key in keys:
        if redis.type(key) == KV:
            table[key] = redis.get(key)

Generatebellmanford()
