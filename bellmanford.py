import redis
import time
import traceback
import datetime
import json

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
graph_price = {}
graph_volume = {}
table = []

def Generatebellmanford():
    print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        table[key] = (json.loads(r.get(key)))
        # valuedump = r.get(key)

def generateGraph(redisvaluetable):
    print("Placeholder")

Generatebellmanford()
print(table)
