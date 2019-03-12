import redis
import time
import traceback
import datetime
import json
import bellman

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
graph_askprice = {}
graph_volume = {}

def generateGraph():
    print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        # Get pair name, bid/ask price and volume then store into bellman_ford readable graph
        pairname = key.decode("utf-8").split('DEPTH',1)[0]
        valuedump = json.loads(r.get(key))
        key1 = pairname[:3]
        key2 = pairname[-3:]
        # Init Json item if it doesnt exist
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
        # Store value into corresponding position
        # Say, HKDJPY need to be saved into {'HKD':{'JPY':PRICE},'JPY':{'HKD':PRICE}}
        graph_askprice[key1].update({key2:float(askprice1)})
        graph_askprice[key2].update({key1:(1/float(askprice2))})
        graph_volume[key1].update({key2:volume1})
        graph_volume[key2].update({key1:volume2})
    return graph_askprice, graph_volume

def generatebellmanford():
    print("Placeholder")

# Generatebellmanford()
graph_askprice, graph_volume = generateGraph()
d, p = bellman.bellman_ford(graph_askprice, 'HKD')
print('Graph Ask Price:')
print(graph_askprice)
print('Graph Volume')
print(graph_volume)
print('Distance = ')
print(d)
print('Predecessor = ')
print(p)
