import redis
import time
import traceback
import datetime
import json

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance

def Generatebellmanford():
    print("Begin table construction")
    keys = r.keys('*')
    table = []
    i = 0
    for key in keys:
        print(json.loads(r.get(key)))
        # valuedump = r.get(key)

Generatebellmanford()
