import redis
import time
import traceback
import datetime
import json
# First approach https://gist.github.com/joninvski/701720
import bellman
# Second approach https://gist.github.com/ngenator/6178728
import bellmanford

# For testing purpose
import os
import datetime
import sys

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
graph_bidprice = {}
graph_bidprice_inverse = {}
graph_volume = {}

def generateGraph():
    # print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        # print('key = ')
        # print(key)
        # print(json.loads(r.get(key)))
        # Get pair name, bid/ask price and volume then store into bellman_ford readable graph
        pairname = key.decode("utf-8").split('DEPTH',1)[0]
        valuedump = json.loads(r.get(key))
        key1 = pairname[:3]
        key2 = pairname[-3:]
        # Init Json item if it doesnt exist
        if not graph_bidprice.get(key1):
            graph_bidprice[key1] = {}
        if not graph_bidprice.get(key2):
            graph_bidprice[key2] = {}
        if not graph_bidprice_inverse.get(key1):
            graph_bidprice_inverse[key1] = {}
        if not graph_bidprice_inverse.get(key2):
            graph_bidprice_inverse[key2] = {}
        if not graph_volume.get(key1):
            graph_volume[key1] = {}
        if not graph_volume.get(key2):
            graph_volume[key2] = {}
        askprice = valuedump['asks'][0][0]
        bidprice = valuedump['bids'][0][0]
        volume1 = valuedump['bids'][0][1]
        volume2 = valuedump['asks'][0][1]
        # Store value into corresponding position
        # Say, HKDJPY need to be saved into {'HKD':{'JPY':PRICE},'JPY':{'HKD':PRICE}}
        graph_bidprice[key1].update({key2:(float(bidprice))})
        graph_bidprice[key2].update({key1:(1/float(askprice))})
        # Use inverse to get shortese path
        graph_bidprice_inverse[key1].update({key2:(1/float(bidprice))})
        graph_bidprice_inverse[key2].update({key1:(float(askprice))})
        graph_volume[key1].update({key2:volume1})
        graph_volume[key2].update({key1:volume2})
    return graph_bidprice, graph_bidprice_inverse, graph_volume
# graph_bidprice sample format
# {
#     "AUD": {
#         "CAD": 0.94746,
#         "CHF": 0.71463,
#         "CNH": 4.75244,
#         "EUR": 0.6278882861161342,
#         "GBP": 0.5340054682159945,
#         "HKD": 5.55071,
#         "JPY": 78.741,
#         "KRW": 803.3741715203856,
#         "NZD": 1.0335,
#         "SGD": 0.95894,
#         "USD": 0.7071,
#         "ZAR": 10.10551
#     },
#     "CAD": {
#         "AUD": 1.0555203715431707,
#         "CHF": 0.75426,
#         "CNH": 5.01585,
#         "EUR": 0.6627168740970483,
#         "GBP": 0.5636279604558623,
#         "JPY": 83.109,
#         "KRW": 847.996608013568,
#         "NZD": 1.0907980278371656,
#         "USD": 0.7463020732271595
#     },
#     "CHF": {
#         "AUD": 1.3993842709207949,
#         "CAD": 1.3258203513423932,
#         "CNH": 6.65011,
#         "CZK": 22.5514,
#         "DKK": 6.55528,
#         "EUR": 0.8786419709696692,
#         "GBP": 0.7472724555372888,
#         "HUF": 277.4,
#         "JPY": 110.186,
#         "KRW": 1124.2270938729623,
#         "NOK": 8.5657,
#         "NZD": 1.4462361703666209,
#         "PLN": 3.7788,
#         "SEK": 9.26938,
#         "USD": 0.9894818083769531,
#         "ZAR": 14.1403
#     },
#     "CNH": {
#         "AUD": 0.21044169607589372,
#         "CAD": 0.19937635077477647,
#         "CHF": 0.15038068871347815,
#         "EUR": 0.13212727556200338,
#         "GBP": 0.11237343941386015,
#         "HKD": 1.16803,
#         "JPY": 16.5698,
#         "SGD": 0.20179272658296304,
#         "USD": 0.1487957956259988
#     },
#     "CZK": {
#         "CHF": 0.04435494602003069,
#         "EUR": 0.03896979451227353,
#         "GBP": 0.033144190486291566,
#         "USD": 0.043886789637451226
#     },
#     "DKK": {
#         "CHF": 0.15255669769669897,
#         "GBP": 0.11400038760131784,
#         "JPY": 16.80994,
#         "NOK": 1.30672,
#         "SEK": 1.41405,
#         "USD": 0.1509486367073876
#     },
#     "EUR": {
#         "AUD": 1.59273,
#         "CAD": 1.509,
#         "CHF": 1.13815,
#         "CNH": 7.56884,
#         "CZK": 25.6651,
#         "GBP": 0.85051,
#         "HKD": 8.8403,
#         "HUF": 315.723,
#         "ILS": 4.0762,
#         "JPY": 125.408,
#         "KRW": 1273.8853503184714,
#         "MXN": 21.8053,
#         "NOK": 9.74896,
#         "NZD": 1.64601,
#         "PLN": 4.30051,
#         "RUB": 74.0533,
#         "SEK": 10.54978,
#         "SGD": 1.52726,
#         "USD": 1.12617,
#         "ZAR": 16.094
#     },
#     "GBP": {
#         "AUD": 1.87273,
#         "CAD": 1.77428,
#         "CHF": 1.33828,
#         "CNH": 8.89946,
#         "CZK": 30.1791,
#         "DKK": 8.7724,
#         "EUR": 1.1757927782807558,
#         "HKD": 10.3945,
#         "HUF": 371.231,
#         "JPY": 147.457,
#         "KRW": 1504.3249341857843,
#         "MXN": 25.6393,
#         "NOK": 11.46303,
#         "NZD": 1.93545,
#         "PLN": 5.0568,
#         "SEK": 12.40455,
#         "SGD": 1.79574,
#         "USD": 1.32417,
#         "ZAR": 18.9236
#     },
#     "HKD": {
#         "AUD": 0.18016751975987272,
#         "CNH": 0.8561643835616439,
#         "EUR": 0.11312038044646353,
#         "GBP": 0.0962084259339433,
#         "JPY": 14.187,
#         "KRW": 144.75969889982628,
#         "USD": 0.12739113153898676
#     },
#     "HUF": {
#         "CHF": 0.003605812569862619,
#         "EUR": 0.003167905317645866,
#         "GBP": 0.0026944736345754857,
#         "USD": 0.0035677334189589353
#     },
#     "ILS": {
#         "EUR": 0.24540479520969838,
#         "USD": 0.276365244306876
#     },
#     "JPY": {
#         "AUD": 0.012700509290422548,
#         "CAD": 0.012032825548095205,
#         "CHF": 0.009075892614038591,
#         "CNH": 0.060352944016609136,
#         "DKK": 0.059491938842286866,
#         "EUR": 0.007974100122801142,
#         "GBP": 0.00678195998643608,
#         "HKD": 0.07049700387733521,
#         "KRW": 10.203535014705844,
#         "MXN": 0.17387675615523718,
#         "NOK": 0.07773879609036047,
#         "NZD": 0.01312559885544778,
#         "SEK": 0.08412551526878102,
#         "SGD": 0.01217833960517823,
#         "USD": 0.008980126978995483,
#         "ZAR": 0.12833675564681726
#     },
#     "KRW": {
#         "AUD": 0.001258,
#         "CAD": 0.00119226,
#         "CHF": 0.000899,
#         "EUR": 0.0007865,
#         "GBP": 0.00067175,
#         "HKD": 0.00698375,
#         "JPY": 0.09905725,
#         "USD": 0.0008855042946958293
#     },
#     "MXN": {
#         "EUR": 0.04586693086018842,
#         "GBP": 0.03901023238395431,
#         "JPY": 5.7521,
#         "USD": 0.05165342617175797
#     },
#     "NOK": {
#         "CHF": 0.11675968521588866,
#         "DKK": 0.765345170671973,
#         "EUR": 0.10258514567090686,
#         "GBP": 0.08724891942213295,
#         "JPY": 12.865,
#         "SEK": 1.08225,
#         "USD": 0.11552840381336156
#     },
#     "NZD": {
#         "AUD": 0.967651413254889,
#         "CAD": 0.91678,
#         "CHF": 0.6915,
#         "EUR": 0.6075629435209488,
#         "GBP": 0.5167130847254445,
#         "JPY": 76.192,
#         "USD": 0.68421
#     },
#     "PLN": {
#         "CHF": 0.2646903123345686,
#         "EUR": 0.23255813953488372,
#         "GBP": 0.19778481012658228,
#         "USD": 0.26189048263797043
#     },
#     "RUB": {
#         "EUR": 0.01350473543548045,
#         "USD": 0.015207138717542455
#     },
#     "SEK": {
#         "CHF": 0.1078946516621171,
#         "DKK": 0.7072485908071828,
#         "EUR": 0.09479823144419418,
#         "GBP": 0.08062435500515996,
#         "JPY": 11.88869,
#         "NOK": 0.9241802521163729,
#         "USD": 0.1067583364916008
#     },
#     "SGD": {
#         "AUD": 1.0428724879808946,
#         "CNH": 4.95603,
#         "EUR": 0.654788797873246,
#         "GBP": 0.5568858940803029,
#         "JPY": 82.115,
#         "USD": 0.7373924328788538
#     },
#     "USD": {
#         "AUD": 1.4142871285728429,
#         "CAD": 1.33996,
#         "CHF": 1.01065,
#         "CNH": 6.72074,
#         "CZK": 22.7901,
#         "DKK": 6.62485,
#         "EUR": 0.8879732897634439,
#         "GBP": 0.755201449986784,
#         "HKD": 7.84986,
#         "HUF": 280.34,
#         "ILS": 3.6193,
#         "JPY": 111.358,
#         "KRW": 1131.008,
#         "MXN": 19.36166,
#         "NOK": 8.65671,
#         "NZD": 1.4615823090077318,
#         "PLN": 3.8188,
#         "RUB": 65.7615,
#         "SEK": 9.36782,
#         "SGD": 1.35616,
#         "ZAR": 14.2912
#     },
#     "ZAR": {
#         "AUD": 0.0989805988128267,
#         "CHF": 0.07072886091169502,
#         "EUR": 0.06214464912820379,
#         "GBP": 0.052852446539750325,
#         "JPY": 7.793,
#         "USD": 0.0699829731426344
#     }
# }

# to generate a nested destination and predecessorgraph
def generatebellmanford(graph):
    ### Upgrade code by updating graph for affected node only
    nested_d = {}
    nested_p = {}
    #
    for base in graph:
        # print('generatebellmanford: run base = ' + base)
        # base = 'HKD'
        d,p = bellmanford.bellman_ford(graph, base)
        # print('d of ' + base + ' = ')
        # print(json.dumps(d,indent=4, sort_keys=True))

        nested_d[base] = d
        nested_p[base] = p
    return nested_d, nested_p

# to Remove all direct predecessor in bellman ford predecessor result
def removedirectprede(p, base):
    # Remove base
    if base in p:
        del p[base]
    # Remove direct predecessor
    for currency in list(p):
        if base in p[currency]:
            p.pop(currency)
    return p

def generateequivalentpricelist(p, base, graph):
    result = {}
    for cur in p:
        if cur==base:
            continue
        tradetimes = 0   # initialize variable
        rate = 1         # initialize variable
        tradestring= cur # initialize variable
        iterator = cur # init loop
        while True:
            tradestring = p[iterator] + ':' + tradestring
            tradetimes +=1
            rate *= graph[p[iterator]][iterator]
            if p[iterator] == base:
                break
            iterator = p[iterator]
        result[cur] = { "rate": rate, "tradetimes": tradetimes, "tradestring": tradestring }
    return result

# Sample result of equivalent pricelist
# {
#     "AUD": {
#         "rate": 0.1801727135632217,
#         "tradestring": "HKD:AUD",
#         "tradetimes": 1
#     },
#     "CAD": {
#         "rate": 0.169516471260772,
#         "tradestring": "HKD:CNH:CAD",
#         "tradetimes": 2
#     },
#     "CHF": {
#         "rate": 0.12788298863290348,
#         "tradestring": "HKD:AUD:CHF",
#         "tradetimes": 2
#     },
#     "CNH": {
#         "rate": 0.8555564111119667,
#         "tradestring": "HKD:CNH",
#         "tradetimes": 1
#     },
#     "CZK": {
#         "rate": 2.886883984488461,
#         "tradestring": "HKD:USD:CZK",
#         "tradetimes": 2
#     },
#     "DKK": {
#         "rate": 0.8392626923018126,
#         "tradestring": "HKD:USD:DKK",
#         "tradetimes": 2
#     },
#     "EUR": {
#         "rate": 0.11248328217218716,
#         "tradestring": "HKD:EUR",
#         "tradetimes": 1
#     },
#     "GBP": {
#         "rate": 0.09609101741169235,
#         "tradestring": "HKD:GBP",
#         "tradetimes": 1
#     },
#     "HUF": {
#         "rate": 35.39686030668999,
#         "tradestring": "HKD:AUD:CHF:HUF",
#         "tradetimes": 3
#     },
#     "ILS": {
#         "rate": 0.45894416442356256,
#         "tradestring": "HKD:EUR:ILS",
#         "tradetimes": 2
#     },
#     "JPY": {
#         "rate": 14.198,
#         "tradestring": "HKD:JPY",
#         "tradetimes": 1
#     },
#     "KRW": {
#         "rate": 145.03331383960835,
#         "tradestring": "HKD:JPY:KRW",
#         "tradetimes": 2
#     },
#     "MXN": {
#         "rate": 2.459511943305461,
#         "tradestring": "HKD:JPY:MXN",
#         "tradetimes": 2
#     },
#     "NOK": {
#         "rate": 1.0921325414923488,
#         "tradestring": "HKD:USD:DKK:NOK",
#         "tradetimes": 3
#     },
#     "NZD": {
#         "rate": 0.18598508530277122,
#         "tradestring": "HKD:AUD:NZD",
#         "tradetimes": 2
#     },
#     "PLN": {
#         "rate": 0.48369097181526804,
#         "tradestring": "HKD:USD:PLN",
#         "tradetimes": 2
#     },
#     "RUB": {
#         "rate": 8.339815369940641,
#         "tradestring": "HKD:EUR:RUB",
#         "tradetimes": 2
#     },
#     "SEK": {
#         "rate": 1.1850389215301593,
#         "tradestring": "HKD:USD:DKK:SEK",
#         "tradetimes": 3
#     },
#     "SGD": {
#         "rate": 0.1725183418182631,
#         "tradestring": "HKD:CNH:SGD",
#         "tradetimes": 2
#     },
#     "USD": {
#         "rate": 0.12739437732176254,
#         "tradestring": "HKD:USD",
#         "tradetimes": 1
#     },
#     "ZAR": {
#         "rate": 1.8399345612704336,
#         "tradestring": "HKD:AUD:ZAR",
#         "tradetimes": 2
#     }
# }

def findtradableprice(pricelist, base, graph):
    order={}
    count=0
    for cur in pricelist:
        items = pricelist[cur]
        if items["tradetimes"] > 1: # tradetimes > 1 means there r shorter path than direct trade
            key1=items["tradestring"][:3]
            key2=items["tradestring"][-3:]
            if graph[key2].get(key1):
                if isworth(float(1/graph[key2][key1])*(1 + (items["tradetimes"]+1)*8/10000),items["rate"]):
                    order[count] = {
                        'tradepair': key1 + ':' + key2,
                        'tradestring': items["tradestring"],
                        'tradetimes' : items["tradetimes"],
                        'equivalentprice' : items["rate"],
                        'reverseprice' : float(1/graph[key2][key1])
                        }
    return order

def isworth(reverseprice, equivalentprice):
    return reverseprice < equivalentprice

def findtradablevolume(tradestring, graph_volume):
    # print(json.dumps(graph_volume,indent=4, sort_keys=True))
    iterator = 0
    items = tradestring.split(':')
    min = graph_volume[items[iterator]][items[iterator+1]]

    # loop thru tradestring one by one to check the minimum volume
    while True:
        if iterator+1 == len(items)-1:
            break
        iterator += 1
        comparator = graph_volume[items[iterator]][items[iterator+1]]
        if min > comparator:
            min = comparator
    return min

def checkKey(dict, key):
    if key in dict:
        return True
    else:
        return False

def looporder(graph_bidprice,graph_volume):
    orders = {}
    count = 0;
    for cur in graph_bidprice:
        for tar in graph_bidprice[cur]:
            # base = tar
            # print(graph_bidprice[cur][tar])
            # Find equivalent price
            for base in graph_bidprice[cur]:
                if base != tar:
                    if checkKey(graph_bidprice[base],tar):
                        if graph_bidprice[cur][base]*graph_bidprice[base][tar]/(1 + 0.0024) > 1/graph_bidprice[tar][cur]:
                            if graph_volume[cur][base] < graph_volume[base][tar]:
                                volume = graph_volume[cur][base]
                            else
                                volume = graph_volume[base][tar]
                            orders[count] = {
                                "tradepair": cur+":"+tar,
                                "tradestring": cur+":"+base+":"+tar,
                                "tradetimes": 2,
                                "equivalentprice": graph_bidprice[cur][base]*graph_bidprice[base][tar],
                                "reverseprice": float(1/graph_bidprice[tar][cur]),
                                "volume": volume
                                }
                            count += 1
    return orders

def wrapper():
    orders = {}
    count = 0;
    graph_bidprice, graph_bidprice_inverse, graph_volume = generateGraph()

    orders = looporder(graph_bidprice,graph_volume)
    # Run for loop checking
    if len(orders) != 0:
        f = open('orders_loop.txt','a')
        # f.write('Test message' + str(datetime.datetime.now()))
        f.write(str(datetime.datetime.now()) + '!' + json.dumps(orders) + '\n')
        f.close()

    # Start BellmanFord
    orders = {}
    # Use inverse to calculate nodes graph_bidprice_inverse
    nested_d, nested_p = generatebellmanford(graph_bidprice)
    # After generated nested bellmanford destination and predecessor json,
    # push into loop to find equivalentprices
    for cur in nested_p:
        equivalentprice = generateequivalentpricelist(nested_p[cur], cur, graph_bidprice)
        order = findtradableprice(equivalentprice, cur, graph_bidprice)
        if len(order) != 0:
            # Push order generated in each iteration into orders array
            for key in order:
                orders[count] = order[key]
                count += 1
    for key in orders:
        orders[key].update({'volume': findtradablevolume(orders[key]['tradestring'],graph_volume)})
    if len(orders) != 0:
        f = open('orders_bellman.txt','a')
        # f.write('Test message' + str(datetime.datetime.now()))
        f.write(str(datetime.datetime.now()) + '!' + json.dumps(orders) + '\n')
        f.close()



def generateorder():
    print('Placeholder')

if __name__ == '__main__':
    orders = {}
    count = 0;
    # graph_bidprice, graph_bidprice_inverse, graph_volume = generateGraph()
    # Write sample data and direct test of functions
    graph_bidprice = {
        "AUD": {
            "CAD": 0.95015,
            "CHF": 0.71049,
            "CNH": 4.78158,
            "EUR": 0.6330355955915401,
            "GBP": 0.53993348019524,
            "HKD": 5.58649,
            "JPY": 79.278,
            "KRW": 805.1529790660226,
            "NZD": 1.04823,
            "SGD": 0.96303,
            "USD": 0.71172,
            "ZAR": 10.09309
        },
        "CAD": {
            "AUD": 1.052454323482361,
            "CHF": 0.74775,
            "CNH": 5.03231,
            "EUR": 0.6662402728920157,
            "GBP": 0.5682528497880417,
            "JPY": 83.436,
            "NZD": 1.1031926394987093,
            "USD": 0.7490019548951022
        },
        "CHF": {
            "AUD": 1.4074397263937173,
            "CAD": 1.3373096005456222,
            "CNH": 6.7305,
            "CZK": 22.9034,
            "DKK": 6.65074,
            "EUR": 0.8910194153130597,
            "GBP": 0.7599361653621095,
            "HUF": 284.95,
            "JPY": 111.583,
            "KRW": 1133.1444759206797,
            "NOK": 8.59105,
            "NZD": 1.4753396969652262,
            "PLN": 3.8248,
            "SEK": 9.2831,
            "USD": 1.00173299808669,
            "ZAR": 14.20619
        },
        "CNH": {
            "AUD": 0.2091232091211179,
            "CAD": 0.19869694543185787,
            "CHF": 0.1485663348685188,
            "EUR": 0.13237809301414327,
            "GBP": 0.11291014610572905,
            "HKD": 1.16829,
            "JPY": 16.5785,
            "SGD": 0.20139810564941824,
            "USD": 0.1488451846350093
        },
        "CZK": {
            "CHF": 0.043653634601616934,
            "EUR": 0.038895371450797356,
            "GBP": 0.033174097664543524,
            "USD": 0.043730949705034744
        },
        "DKK": {
            "CHF": 0.15035333032626674,
            "EUR": 0.13396762538364979,
            "GBP": 0.11426064223621787,
            "JPY": 16.77701,
            "NOK": 1.29173,
            "SEK": 1.39582,
            "USD": 0.15061851493156647
        },
        "EUR": {
            "AUD": 1.57965,
            "CAD": 1.50092,
            "CHF": 1.1223,
            "CNH": 7.55376,
            "CZK": 25.7042,
            "DKK": 7.46439,
            "GBP": 0.8529,
            "HKD": 8.82534,
            "HUF": 319.811,
            "ILS": 4.0468,
            "JPY": 125.235,
            "KRW": 1277.5471095496646,
            "MXN": 21.6275,
            "NOK": 9.64202,
            "NZD": 1.65583,
            "PLN": 4.29279,
            "RUB": 73.4503,
            "SEK": 10.4193,
            "SGD": 1.52123,
            "USD": 1.12429,
            "ZAR": 15.9438
        },
        "GBP": {
            "AUD": 1.85201,
            "CAD": 1.75968,
            "CHF": 1.31582,
            "CNH": 8.85589,
            "CZK": 30.136,
            "DKK": 8.75109,
            "EUR": 1.1724016648103641,
            "HKD": 10.34659,
            "HUF": 374.94,
            "JPY": 146.825,
            "MXN": 25.3568,
            "NOK": 11.30469,
            "NZD": 1.9414,
            "PLN": 5.0328,
            "SEK": 12.21502,
            "SGD": 1.7836,
            "USD": 1.31814,
            "ZAR": 18.69269
        },
        "HKD": {
            "AUD": 0.17899654536667442,
            "CNH": 0.8559152301556054,
            "EUR": 0.11330789948682853,
            "GBP": 0.096645343482383,
            "JPY": 14.19,
            "KRW": 144.1023933966519,
            "USD": 0.12740216787528855
        },
        "HUF": {
            "CHF": 0.0035087719298245615,
            "EUR": 0.0031262993681748976,
            "GBP": 0.002666453350398635,
            "USD": 0.0035149384885764497
        },
        "ILS": {
            "EUR": 0.24704716871592292,
            "USD": 0.2777469170092212
        },
        "JPY": {
            "AUD": 0.012613362596334556,
            "CAD": 0.011984803269454333,
            "CHF": 0.008961697704013049,
            "CNH": 0.06031723245235994,
            "DKK": 0.05960185957801884,
            "EUR": 0.007984924462614583,
            "GBP": 0.006810458139519046,
            "HKD": 0.07046719751955464,
            "KRW": 10.155222577090832,
            "MXN": 0.1726963600788186,
            "NOK": 0.0769941484447182,
            "NZD": 0.013221916649037444,
            "SEK": 0.08319342971569478,
            "SGD": 0.01214742110249994,
            "USD": 0.008977385964754782,
            "ZAR": 0.12732365673542145
        },
        "KRW": {
            "AUD": 0.00122925,
            "CHF": 0.0008735,
            "EUR": 0.00078175,
            "HKD": 0.00686674,
            "JPY": 0.09746125,
            "USD": 0.0008790011031463845
        },
        "MXN": {
            "EUR": 0.04622543869096954,
            "GBP": 0.03942671972451762,
            "JPY": 5.789,
            "USD": 0.05197370130713858
        },
        "NOK": {
            "CHF": 0.11638869167471687,
            "DKK": 0.7741016550293385,
            "EUR": 0.10370259754266324,
            "GBP": 0.08844861135680171,
            "JPY": 12.9874,
            "SEK": 1.0805,
            "USD": 0.116592921643727
        },
        "NZD": {
            "AUD": 0.9539345028570339,
            "CAD": 0.90639,
            "CHF": 0.67775,
            "EUR": 0.6038793207565399,
            "GBP": 0.515089548317975,
            "JPY": 75.63,
            "USD": 0.67896
        },
        "PLN": {
            "CHF": 0.2614174051708363,
            "EUR": 0.23292974373069594,
            "GBP": 0.1986610246935654,
            "USD": 0.2618801950483693
        },
        "RUB": {
            "EUR": 0.013612570719006456,
            "USD": 0.015300788250708311
        },
        "SEK": {
            "CHF": 0.1077110328410939,
            "DKK": 0.7163477725166014,
            "EUR": 0.09596882932423549,
            "GBP": 0.08185315543914218,
            "JPY": 12.01826,
            "NOK": 0.9253689908851154,
            "USD": 0.10789628146255567
        },
        "SGD": {
            "AUD": 1.0383461222964063,
            "CNH": 4.96496,
            "EUR": 0.657323902926406,
            "GBP": 0.5606323933396872,
            "JPY": 82.32,
            "USD": 0.7390272922779039
        },
        "USD": {
            "AUD": 1.4050074465394666,
            "CAD": 1.33509,
            "CHF": 0.99825,
            "CNH": 6.71823,
            "CZK": 22.864,
            "DKK": 6.63921,
            "EUR": 0.8894423196655696,
            "GBP": 0.7586217360299807,
            "HKD": 7.8491,
            "HUF": 284.459,
            "ILS": 3.5994,
            "JPY": 111.39,
            "KRW": 1136.414,
            "MXN": 19.23749,
            "NOK": 8.57616,
            "NZD": 1.4727974314412795,
            "PLN": 3.8182,
            "RUB": 65.34809,
            "SEK": 9.26749,
            "SGD": 1.35309,
            "ZAR": 14.18122
        },
        "ZAR": {
            "AUD": 0.09905197356104721,
            "CHF": 0.07037446251504255,
            "EUR": 0.0627053207345803,
            "GBP": 0.05348305736967115,
            "JPY": 7.853,
            "USD": 0.07050296817496017
        }
    }

    graph_bidprice_inverse = {
        "AUD": {
            "CAD": 1.0524654001999683,
            "CHF": 1.4074793452406087,
            "CNH": 0.20913589232011176,
            "EUR": 1.57969,
            "GBP": 1.85208,
            "HKD": 0.1790032739698809,
            "JPY": 0.012613839905143923,
            "KRW": 0.001242,
            "NZD": 0.9539891054444158,
            "SGD": 1.0383892505944778,
            "USD": 1.405046928567414,
            "ZAR": 0.0990776858226767
        },
        "CAD": {
            "AUD": 0.95016,
            "CHF": 1.3373453694416582,
            "CNH": 0.19871589786797714,
            "EUR": 1.50096,
            "GBP": 1.75978,
            "JPY": 0.0119852341914761,
            "NZD": 0.90646,
            "USD": 1.33511
        },
        "CHF": {
            "AUD": 0.71051,
            "CAD": 0.74777,
            "CNH": 0.14857737166629523,
            "CZK": 0.04366163975654269,
            "DKK": 0.1503592081482662,
            "EUR": 1.12231,
            "GBP": 1.3159,
            "HUF": 0.00350938761186173,
            "JPY": 0.008961938646568026,
            "KRW": 0.0008825,
            "NOK": 0.11640020719236881,
            "NZD": 0.67781,
            "PLN": 0.26145157916753814,
            "SEK": 0.10772263575745172,
            "USD": 0.99827,
            "ZAR": 0.07039185031313815
        },
        "CNH": {
            "AUD": 4.78187,
            "CAD": 5.03279,
            "CHF": 6.731,
            "EUR": 7.55412,
            "GBP": 8.8566,
            "HKD": 0.8559518612673223,
            "JPY": 0.06031908797538982,
            "SGD": 4.96529,
            "USD": 6.71839
        },
        "CZK": {
            "CHF": 22.9076,
            "EUR": 25.71,
            "GBP": 30.144,
            "USD": 22.8671
        },
        "DKK": {
            "CHF": 6.651,
            "EUR": 7.46449,
            "GBP": 8.75192,
            "JPY": 0.05960537664339474,
            "NOK": 0.7741555897904361,
            "SEK": 0.716424753908097,
            "USD": 6.63929
        },
        "EUR": {
            "AUD": 0.6330516253600481,
            "CAD": 0.6662580284092423,
            "CHF": 0.8910273545397843,
            "CNH": 0.1323844019402258,
            "CZK": 0.03890414796025552,
            "DKK": 0.1339694201401588,
            "GBP": 1.1724703951225233,
            "HKD": 0.11331008210448548,
            "HUF": 0.00312684679388764,
            "ILS": 0.24710882672729068,
            "JPY": 0.007984988222142372,
            "KRW": 0.00078275,
            "MXN": 0.04623742919893654,
            "NOK": 0.10371270750319954,
            "NZD": 0.6039267316089212,
            "PLN": 0.23294873497189472,
            "RUB": 0.013614648272369207,
            "SEK": 0.09597573733360207,
            "SGD": 0.6573627919512499,
            "USD": 0.8894502308123349,
            "ZAR": 0.06272030507156387
        },
        "GBP": {
            "AUD": 0.5399538879379702,
            "CAD": 0.5682851427532278,
            "CHF": 0.7599823684090529,
            "CNH": 0.11291919840919433,
            "CZK": 0.03318290416777277,
            "DKK": 0.1142714793242899,
            "EUR": 0.85295,
            "HKD": 0.09665020069414174,
            "HUF": 0.0026670934016109244,
            "JPY": 0.006810829218457348,
            "MXN": 0.039437152953054014,
            "NOK": 0.0884588608798649,
            "NZD": 0.5150922015040692,
            "PLN": 0.1986965506278811,
            "SEK": 0.08186642346881134,
            "SGD": 0.5606638259699483,
            "USD": 0.7586447570060842,
            "ZAR": 0.053496848233186345
        },
        "HKD": {
            "AUD": 5.5867,
            "CNH": 1.16834,
            "EUR": 8.82551,
            "GBP": 10.34711,
            "JPY": 0.07047216349541931,
            "KRW": 0.00693951,
            "USD": 7.84916
        },
        "HUF": {
            "CHF": 285.0,
            "EUR": 319.867,
            "GBP": 375.03,
            "USD": 284.5
        },
        "ILS": {
            "EUR": 4.04781,
            "USD": 3.6004
        },
        "JPY": {
            "AUD": 79.281,
            "CAD": 83.439,
            "CHF": 111.586,
            "CNH": 16.57901,
            "DKK": 16.778,
            "EUR": 125.236,
            "GBP": 146.833,
            "HKD": 14.191,
            "KRW": 0.0984715,
            "MXN": 5.79051,
            "NOK": 12.988,
            "NZD": 75.632,
            "SEK": 12.02018,
            "SGD": 82.322,
            "USD": 111.391,
            "ZAR": 7.854
        },
        "KRW": {
            "AUD": 813.5041692088671,
            "CHF": 1144.8196908986833,
            "EUR": 1279.1813239526703,
            "HKD": 145.62951269452464,
            "JPY": 10.260488142723391,
            "USD": 1137.655
        },
        "MXN": {
            "EUR": 21.63311,
            "GBP": 25.36351,
            "JPY": 0.1727414061150458,
            "USD": 19.2405
        },
        "NOK": {
            "CHF": 8.5919,
            "DKK": 1.29182,
            "EUR": 9.64296,
            "GBP": 11.306,
            "JPY": 0.07699770546837705,
            "SEK": 0.9254974548819991,
            "USD": 8.57685
        },
        "NZD": {
            "AUD": 1.04829,
            "CAD": 1.1032778384580588,
            "CHF": 1.4754703061600887,
            "EUR": 1.65596,
            "GBP": 1.94141,
            "JPY": 0.013222266296443212,
            "USD": 1.4728408153646753
        },
        "PLN": {
            "CHF": 3.8253,
            "EUR": 4.29314,
            "GBP": 5.0337,
            "USD": 3.81854
        },
        "RUB": {
            "EUR": 73.46151,
            "USD": 65.35611
        },
        "SEK": {
            "CHF": 9.2841,
            "DKK": 1.39597,
            "EUR": 10.42005,
            "GBP": 12.217,
            "JPY": 0.08320672044039654,
            "NOK": 1.08065,
            "USD": 9.26816
        },
        "SGD": {
            "AUD": 0.96307,
            "CNH": 0.20141149173407238,
            "EUR": 1.52132,
            "GBP": 1.7837,
            "JPY": 0.012147716229348883,
            "USD": 1.35313
        },
        "USD": {
            "AUD": 0.71174,
            "CAD": 0.7490131751417507,
            "CHF": 1.0017530678687703,
            "CNH": 0.14884872950166933,
            "CZK": 0.043736878936319105,
            "DKK": 0.15062032982839826,
            "EUR": 1.1243,
            "GBP": 1.31818,
            "HKD": 0.12740314176147585,
            "HUF": 0.0035154451080823598,
            "ILS": 0.27782408179140966,
            "JPY": 0.008977466558937068,
            "KRW": 0.0008799610001284743,
            "MXN": 0.051981833388867256,
            "NOK": 0.11660230219585456,
            "NZD": 0.67898,
            "PLN": 0.2619035147451679,
            "RUB": 0.015302666076391828,
            "SEK": 0.10790408190351432,
            "SGD": 0.7390491393772772,
            "ZAR": 0.07051579483288462
        },
        "ZAR": {
            "AUD": 10.09571,
            "CHF": 14.2097,
            "EUR": 15.94761,
            "GBP": 18.69751,
            "JPY": 0.12733987011333248,
            "USD": 14.1838
        }
    }


    graph_volume = {
        "AUD": {
            "CAD": "1000000",
            "CHF": "1000000",
            "CNH": "1000000",
            "EUR": "500000",
            "GBP": "2000000",
            "HKD": "1000000",
            "JPY": "3000000",
            "KRW": "100000000",
            "NZD": "1000000",
            "SGD": "1000000",
            "USD": "5000000",
            "ZAR": "1000000"
        },
        "CAD": {
            "AUD": "1000000",
            "CHF": "1300000",
            "CNH": "1000000",
            "EUR": "2400000",
            "GBP": "800000",
            "JPY": "5500000",
            "NZD": "1000000",
            "USD": "1000000"
        },
        "CHF": {
            "AUD": "3000000",
            "CAD": "2000000",
            "CNH": "2000000",
            "CZK": "1000000",
            "DKK": "1000000",
            "EUR": "1000000",
            "GBP": "1000000",
            "HUF": "2000000",
            "JPY": "1000000",
            "KRW": "100000000",
            "NOK": "1000000",
            "NZD": "1000000",
            "PLN": "2000000",
            "SEK": "1000000",
            "USD": "2000000",
            "ZAR": "1000000"
        },
        "CNH": {
            "AUD": "2000000",
            "CAD": "1000000",
            "CHF": "2000000",
            "EUR": "2000000",
            "GBP": "2000000",
            "HKD": "1000000",
            "JPY": "1000000",
            "SGD": "1000000",
            "USD": "1000000"
        },
        "CZK": {
            "CHF": "2000000",
            "EUR": "1000000",
            "GBP": "2000000",
            "USD": "1000000"
        },
        "DKK": {
            "CHF": "1000000",
            "EUR": "3000000",
            "GBP": "1000000",
            "JPY": "1000000",
            "NOK": "14000000",
            "SEK": "14000000",
            "USD": "2000000"
        },
        "EUR": {
            "AUD": "600000",
            "CAD": "2000000",
            "CHF": "1000000",
            "CNH": "1000000",
            "CZK": "2000000",
            "DKK": "3000000",
            "GBP": "2000000",
            "HKD": "1000000",
            "HUF": "2000000",
            "ILS": "1000000",
            "JPY": "2000000",
            "KRW": "100000000",
            "MXN": "1000000",
            "NOK": "2000000",
            "NZD": "3600000",
            "PLN": "1000000",
            "RUB": "1000000",
            "SEK": "500000",
            "SGD": "2400000",
            "USD": "2000000",
            "ZAR": "1000000"
        },
        "GBP": {
            "AUD": "500000",
            "CAD": "1000000",
            "CHF": "800000",
            "CNH": "1000000",
            "CZK": "2000000",
            "DKK": "1900000",
            "EUR": "4500000",
            "HKD": "2000000",
            "HUF": "2000000",
            "JPY": "4000000",
            "MXN": "800000",
            "NOK": "1000000",
            "NZD": "500000",
            "PLN": "1000000",
            "SEK": "1000000",
            "SGD": "2000000",
            "USD": "1000000",
            "ZAR": "1000000"
        },
        "HKD": {
            "AUD": "1000000",
            "CNH": "3000000",
            "EUR": "1000000",
            "GBP": "800000",
            "JPY": "42000000",
            "KRW": "100000000",
            "USD": "2000000"
        },
        "HUF": {
            "CHF": "1000000",
            "EUR": "2000000",
            "GBP": "2000000",
            "USD": "2000000"
        },
        "ILS": {
            "EUR": "900000",
            "USD": "1000000"
        },
        "JPY": {
            "AUD": "1000000",
            "CAD": "1300000",
            "CHF": "1000000",
            "CNH": "1000000",
            "DKK": "33000000",
            "EUR": "2000000",
            "GBP": "800000",
            "HKD": "43000000",
            "KRW": "100000000",
            "MXN": "19000000",
            "NOK": "9000000",
            "NZD": "2000000",
            "SEK": "1000000",
            "SGD": "1000000",
            "USD": "1000000",
            "ZAR": "13000000"
        },
        "KRW": {
            "AUD": "100000000",
            "CHF": "100000000",
            "EUR": "100000000",
            "HKD": "100000000",
            "JPY": "100000000",
            "USD": "100000"
        },
        "MXN": {
            "EUR": "2000000",
            "GBP": "800000",
            "JPY": "11000000",
            "USD": "1000000"
        },
        "NOK": {
            "CHF": "1000000",
            "DKK": "7000000",
            "EUR": "1000000",
            "GBP": "1000000",
            "JPY": "8000000",
            "SEK": "20000000",
            "USD": "1000000"
        },
        "NZD": {
            "AUD": "1000000",
            "CAD": "1000000",
            "CHF": "2000000",
            "EUR": "1000000",
            "GBP": "1000000",
            "JPY": "2000000",
            "USD": "500000"
        },
        "PLN": {
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "2900000",
            "USD": "1000000"
        },
        "RUB": {
            "EUR": "900000",
            "USD": "1000000"
        },
        "SEK": {
            "CHF": "1000000",
            "DKK": "1000000",
            "EUR": "1000000",
            "GBP": "900000",
            "JPY": "1000000",
            "NOK": "10000000",
            "USD": "1000000"
        },
        "SGD": {
            "AUD": "1000000",
            "CNH": "1000000",
            "EUR": "900000",
            "GBP": "3000000",
            "JPY": "500000",
            "USD": "1000000"
        },
        "USD": {
            "AUD": "1000000",
            "CAD": "1000000",
            "CHF": "1000000",
            "CNH": "1000000",
            "CZK": "2000000",
            "DKK": "1100000",
            "EUR": "9000000",
            "GBP": "1000000",
            "HKD": "1000000",
            "HUF": "1000000",
            "ILS": "1000000",
            "JPY": "3000000",
            "KRW": "100000",
            "MXN": "1000000",
            "NOK": "1100000",
            "NZD": "2000000",
            "PLN": "2100000",
            "RUB": "1000000",
            "SEK": "500000",
            "SGD": "4500000",
            "ZAR": "1000000"
        },
        "ZAR": {
            "AUD": "500000",
            "CHF": "2000000",
            "EUR": "500000",
            "GBP": "800000",
            "JPY": "44000000",
            "USD": "500000"
        }
    }

    # Use inverse to calculate nodes graph_bidprice_inverse
    nested_d, nested_p = generatebellmanford(graph_bidprice)
    # After generated nested bellmanford destination and predecessor json,
    # push into loop to find equivalentprices
    for cur in nested_p:
        equivalentprice = generateequivalentpricelist(nested_p[cur], cur, graph_bidprice)
        order = findtradableprice(equivalentprice, cur, graph_bidprice)
        if len(order) != 0:
            # Push order generated in each iteration into orders array
            for key in order:
                orders[count] = order[key]
                count += 1
    for key in orders:
        orders[key].update({'volume': findtradablevolume(orders[key]['tradestring'],graph_volume)})
    f = open('orders.txt','w')
    f.write(str(datetime.datetime.now()) + ': ' + json.dumps(orders,indent=4, sort_keys=True) + '\n')
    f.close()
    # print('Orders after append = ')
    # print(orders)
