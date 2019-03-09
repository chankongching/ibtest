import redis
import time
import traceback
import datetime
import json

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
graph_askprice = {}
graph_volume = {}

def generateGraph():
    print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        pairname = key.decode("utf-8").split('DEPTH',1)[0]
        valuedump = json.loads(r.get(key))
        key1 = pairname[:3]
        key2 = pairname[-3:]
        if not graph_askprice.get(key1):
            graph_askprice[key1] = {}
        if not graph_askprice.get(key2):
            graph_askprice[key2] = {}
        if not graph_volume.get(key1):
            graph_volume[key1] = {}
        if not graph_volume.get(key2):
            graph_volume[key2] = {}
        askprice1 = valuedump['asks'][0][0]
        askprice2 = valuedump['bids'][0][0]
        volume1 = valuedump['asks'][0][1]
        volume2 = valuedump['bids'][0][1]

        # print(valuedump)
        # print(key1 + ':' + key2)
        graph_askprice[key1].update({key2:float(askprice1)})
        graph_askprice[key2].update({key1:(1/float(askprice2))})
        graph_volume[key1].update({key2:volume1})
        graph_volume[key2].update({key1.volume2})

        # graph_askprice[key1].update({key2:valuedump['ask'][0][0][1]})
        # # table[key] = (json.loads(r.get(key)))
        # # valuedump = r.get(key)

def Generatebellmanford():
    print("Placeholder")

# Generatebellmanford()
generateGraph()
print(graph_askprice)
print(graph_volume)
