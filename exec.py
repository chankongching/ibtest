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
import math

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
# graph_bidprice = {}
# graph_bidprice_inverse = {}
# graph_volume = {}

def generateGraph():
    graph_bidprice = {}
    graph_bidprice_inverse = {}
    graph_bidprice_minuslog = {}
    graph_volume = {}
    # print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        # print('key = ')
        # print(key)
        # print(json.loads(r.get(key)))
        # Get pair name, bid/ask price and volume then store into bellman_ford readable graph
        pairname = key.decode("utf-8").split('DEPTH',1)[0]
        value = r.get(key)
        if value is not None:
            valuedump = json.loads(value)
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
            if not graph_bidprice_minuslog.get(key1):
                graph_bidprice_minuslog[key1] = {}
            if not graph_bidprice_minuslog.get(key2):
                graph_bidprice_minuslog[key2] = {}
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
            graph_bidprice_minuslog[key1].update({key2:(-1 * math.log10(float(bidprice)))})
            graph_bidprice_minuslog[key2].update({key1:(-1 * math.log10(1/float(askprice)))})
            # Use inverse to get shortese path
            graph_bidprice_inverse[key1].update({key2:(1/float(bidprice))})
            graph_bidprice_inverse[key2].update({key1:(float(askprice))})
            graph_volume[key1].update({key2:volume1})
            graph_volume[key2].update({key1:volume2})
    return graph_bidprice, graph_bidprice_minuslog, graph_bidprice_inverse, graph_volume
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
    print("p = ", end='')
    print(p)
    print("base = ", end="")
    print(json.dumps(base,indent=4, sort_keys=True))
    print("graph = ", end="")
    print(json.dumps(graph,indent=4, sort_keys=True))
    for cur in p:
        if cur==base:
            continue
        print('Cur = ', end='')
        print(cur)
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
                print("tradestring",end='')
                print(items["tradestring"])
                print("Equivalentprice = ",end='')
                print(items["rate"])
                if isworth(float(1/graph[key2][key1])*(1 + (items["tradetimes"]+1)*2/100000),items["rate"]):
                    order[count] = {
                        'tradepair': key1 + ':' + key2,
                        'tradestring': items["tradestring"],
                        'tradetimes' : items["tradetimes"],
                        'equivalentprice' : items["rate"],
                        'reverseprice' : float(1/graph[key2][key1])
                        }
    return order

def isworth(reverseprice, equivalentprice):
    if reverseprice != -1:
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
                        if ((graph_bidprice[tar][cur] != -1 and graph_bidprice[cur][tar] != -1 )) and (graph_bidprice[cur][base]*graph_bidprice[base][tar] > (1/graph_bidprice[tar][cur])*(1 + 6/100000)):
                            if graph_volume[cur][base] < graph_volume[base][tar]:
                                volume = graph_volume[cur][base]
                            else:
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
        # f.close()
        # f = open('orders_loop_pricecheck.txt','a')
        # # Print result for checking
        # f.write(str("graph_bidprice = " + '\n'))
        # f.write(str(json.dumps(graph_bidprice,indent=4, sort_keys=True) + '\n'))
        # f.write(str("graph_bidprice_inverse = " + '\n'))
        # f.write(str(json.dumps(graph_bidprice_inverse,indent=4, sort_keys=True) + '\n'))
        # f.write(str("graph_volumn = " + '\n'))
        # f.write(str(json.dumps(graph_volumn,indent=4, sort_keys=True) + '\n'))
        # f.close()

    # Start BellmanFord
    orders = {}
    # Use inverse to calculate nodes graph_bidprice_inverse
    nested_d, nested_p = generatebellmanford(graph_bidprice_inverse)
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
        f = open('orders_bellman_pricecheck.txt','a')
        # Print result for checking
        f.write(str("graph_bidprice = " + '\n'))
        f.write(str(json.dumps(graph_bidprice,indent=4, sort_keys=True) + '\n'))
        f.close()



def generateorder():
    print('Placeholder')

if __name__ == '__main__':
    orders = {}
    count = 0;
    graph_bidprice, graph_bidprice_minuslog, graph_bidprice_inverse, graph_volume = generateGraph()
    # Write sample data and direct test of functions
    # graph_bidprice = {
    #     "AUD": {
    #         "CAD": 0.94888,
    #         "CHF": 0.7085,
    #         "CNH": 4.7711,
    #         "EUR": 0.6317997447529031,
    #         "GBP": 0.5431387991201151,
    #         "HKD": 5.56772,
    #         "JPY": 79.032,
    #         "NZD": 1.05384,
    #         "SGD": 0.96206,
    #         "USD": 0.7093,
    #         "ZAR": 10.0388
    #     },
    #     "CAD": {
    #         "AUD": 1.0538185113759708,
    #         "CHF": 0.74666,
    #         "CNH": 5.02791,
    #         "EUR": 0.6658277237347608,
    #         "GBP": 0.5723934632666495,
    #         "JPY": 83.289,
    #         "KRW": 850.7018290089325,
    #         "NZD": 1.1105311670572036,
    #         "USD": 0.7474679523115446
    #     },
    #     "CHF": {
    #         "AUD": 1.4113529229119035,
    #         "CAD": 1.3392259274139546,
    #         "CNH": 6.734,
    #         "CZK": 22.8652,
    #         "DKK": 6.65689,
    #         "EUR": 0.8917265609673449,
    #         "GBP": 0.7665889856494541,
    #         "HUF": 286.299,
    #         "JPY": 111.545,
    #         "KRW": 1139.6011396011395,
    #         "NOK": 8.61464,
    #         "NZD": 1.4873205919535957,
    #         "PLN": 3.8274,
    #         "SEK": 9.3049,
    #         "USD": 1.0010911893964423,
    #         "ZAR": 14.16909
    #     },
    #     "CNH": {
    #         "AUD": 0.20957857939255742,
    #         "CAD": 0.19887397555043343,
    #         "CHF": 0.1484891231717277,
    #         "EUR": 0.13241911178556579,
    #         "GBP": 0.11383816766085333,
    #         "HKD": 1.16693,
    #         "JPY": 16.56439,
    #         "SGD": 0.20163688825888562,
    #         "USD": 0.14866174695392081
    #     },
    #     "CZK": {
    #         "CHF": 0.043719287200741475,
    #         "EUR": 0.03898924286789275,
    #         "GBP": 0.03351655717924655,
    #         "USD": 0.043767507002801125
    #     },
    #     "DKK": {
    #         "CHF": 0.1502085645919359,
    #         "EUR": 0.13395291019395042,
    #         "GBP": 0.11515231772827507,
    #         "JPY": 16.756,
    #         "NOK": 1.29408,
    #         "SEK": 1.39773,
    #         "USD": 0.15038046257030288
    #     },
    #     "EUR": {
    #         "AUD": 1.5827,
    #         "CAD": 1.50183,
    #         "CHF": 1.12135,
    #         "CNH": 7.55126,
    #         "CZK": 25.6392,
    #         "DKK": 7.46522,
    #         "GBP": 0.85963,
    #         "HKD": 8.81225,
    #         "ILS": 4.0244,
    #         "JPY": 125.088,
    #         "MXN": 21.4435,
    #         "NOK": 9.66119,
    #         "NZD": 1.66789,
    #         "PLN": 4.29199,
    #         "RUB": 73.1555,
    #         "SEK": 10.43449,
    #         "SGD": 1.52268,
    #         "USD": 1.12263,
    #         "ZAR": 15.8885
    #     },
    #     "GBP": {
    #         "AUD": 1.84102,
    #         "CAD": 1.74686,
    #         "CHF": 1.30435,
    #         "CNH": 8.7837,
    #         "CZK": 29.825,
    #         "DKK": 8.68319,
    #         "EUR": 1.1631964638827497,
    #         "HKD": 10.25039,
    #         "HUF": 373.45,
    #         "JPY": 145.498,
    #         "KRW": 1486.4362690449648,
    #         "MXN": 24.943,
    #         "NOK": 11.23705,
    #         "NZD": 1.94021,
    #         "PLN": 4.992,
    #         "SEK": 12.137,
    #         "SGD": 1.77116,
    #         "USD": 1.30604,
    #         "ZAR": 18.4806
    #     },
    #     "HKD": {
    #         "AUD": 0.17960157187295703,
    #         "CNH": 0.8569127148708633,
    #         "EUR": 0.1134764649811629,
    #         "GBP": 0.09755136323152547,
    #         "JPY": 14.194,
    #         "KRW": 144.9903653902198,
    #         "USD": 0.1273950264981655
    #     },
    #     "HUF": {
    #         "CHF": 0.0034917298378789835,
    #         "GBP": 0.002676652364420866,
    #         "USD": 0.0034956356988300103
    #     },
    #     "ILS": {
    #         "EUR": 0.2483972169575812,
    #         "USD": 0.2788770180238217
    #     },
    #     "JPY": {
    #         "AUD": 0.012652302086364612,
    #         "CAD": 0.012005810812433217,
    #         "CHF": 0.008964429145152036,
    #         "CNH": 0.060368209859215295,
    #         "DKK": 0.059676553082293964,
    #         "EUR": 0.00799411633038084,
    #         "GBP": 0.0068724271350913005,
    #         "HKD": 0.07044734061289186,
    #         "KRW": 10.215807920744945,
    #         "MXN": 0.1714380739961015,
    #         "NOK": 0.0772278298207542,
    #         "NZD": 0.013334044482372394,
    #         "SEK": 0.08341675008341676,
    #         "SGD": 0.012172854534388313,
    #         "USD": 0.008974646623289208,
    #         "ZAR": 0.12703252032520326
    #     },
    #     "KRW": {
    #         "CAD": 0.001163,
    #         "CHF": 0.0008685,
    #         "GBP": 0.00066575,
    #         "HKD": 0.00682399,
    #         "JPY": 0.0968775,
    #         "USD": 0.0008735226548100525
    #     },
    #     "MXN": {
    #         "EUR": 0.04662002488576929,
    #         "GBP": 0.04008046554262337,
    #         "JPY": 5.83199,
    #         "USD": 0.05234053800839018
    #     },
    #     "NOK": {
    #         "CHF": 0.11606448542810385,
    #         "DKK": 0.7726184037703778,
    #         "EUR": 0.10349824052991098,
    #         "GBP": 0.08897272096375251,
    #         "JPY": 12.94699,
    #         "SEK": 1.08002,
    #         "USD": 0.11619179081759515
    #     },
    #     "NZD": {
    #         "AUD": 0.9488746346832657,
    #         "CAD": 0.90036,
    #         "CHF": 0.67227,
    #         "EUR": 0.5995096011462624,
    #         "GBP": 0.5153603141636475,
    #         "JPY": 74.993,
    #         "USD": 0.67305
    #     },
    #     "PLN": {
    #         "CHF": 0.26120572562950584,
    #         "EUR": 0.2329367972587998,
    #         "GBP": 0.20024028834601523,
    #         "USD": 0.26149943777620877
    #     },
    #     "RUB": {
    #         "EUR": 0.01362523862902304,
    #         "USD": 0.015294025343117636
    #     },
    #     "SEK": {
    #         "CHF": 0.10745397477625396,
    #         "DKK": 0.7153280494434747,
    #         "EUR": 0.09582178680802296,
    #         "GBP": 0.08237503706876668,
    #         "JPY": 11.98577,
    #         "NOK": 0.9257287799820408,
    #         "USD": 0.10757395978670235
    #     },
    #     "SGD": {
    #         "AUD": 1.039371388184426,
    #         "CNH": 4.95906,
    #         "EUR": 0.6567023037116815,
    #         "GBP": 0.5645571049511657,
    #         "JPY": 82.146,
    #         "USD": 0.7372510856022235
    #     },
    #     "USD": {
    #         "AUD": 1.4098009361078216,
    #         "CAD": 1.3378,
    #         "CHF": 0.99886,
    #         "CNH": 6.72652,
    #         "CZK": 22.839,
    #         "DKK": 6.64968,
    #         "EUR": 0.8907495657595867,
    #         "GBP": 0.7656557458635448,
    #         "HKD": 7.84959,
    #         "HUF": 285.98,
    #         "ILS": 3.5846,
    #         "JPY": 111.424,
    #         "KRW": 1143.536,
    #         "MXN": 19.1019,
    #         "NOK": 8.6055,
    #         "NZD": 1.4857074939085992,
    #         "PLN": 3.823,
    #         "RUB": 65.2116,
    #         "SEK": 9.2945,
    #         "SGD": 1.35636,
    #         "ZAR": 14.1533
    #     },
    #     "ZAR": {
    #         "AUD": 0.09958661595716181,
    #         "CHF": 0.0705581858079265,
    #         "EUR": 0.06292232679213798,
    #         "GBP": 0.05409411293768899,
    #         "JPY": 7.87,
    #         "USD": 0.07063643427279791
    #     }
    # }
    #
    # graph_bidprice_inverse = {
    #     "AUD": {
    #         "CAD": 1.0538740409746228,
    #         "CHF": 1.4114326040931544,
    #         "CNH": 0.20959527153067428,
    #         "EUR": 1.58278,
    #         "GBP": 1.84115,
    #         "HKD": 0.17960673309721037,
    #         "JPY": 0.012653102540742991,
    #         "NZD": 0.948910650573142,
    #         "SGD": 1.0394362097998047,
    #         "USD": 1.4098406880022556,
    #         "ZAR": 0.0996134996214687
    #     },
    #     "CAD": {
    #         "AUD": 0.94893,
    #         "CHF": 1.3392976723006456,
    #         "CNH": 0.19888979715229588,
    #         "EUR": 1.50189,
    #         "GBP": 1.74705,
    #         "JPY": 0.012006387398095788,
    #         "KRW": 0.0011755,
    #         "NZD": 0.90047,
    #         "USD": 1.33785
    #     },
    #     "CHF": {
    #         "AUD": 0.70854,
    #         "CAD": 0.7467,
    #         "CNH": 0.1485001485001485,
    #         "CZK": 0.04373458355929535,
    #         "DKK": 0.15022029806711543,
    #         "EUR": 1.12142,
    #         "GBP": 1.30448,
    #         "HUF": 0.0034928518786303832,
    #         "JPY": 0.00896499170738267,
    #         "KRW": 0.0008775,
    #         "NOK": 0.11608146132630034,
    #         "NZD": 0.67235,
    #         "PLN": 0.26127397188692064,
    #         "SEK": 0.10747025760620749,
    #         "USD": 0.99891,
    #         "ZAR": 0.07057616261877085
    #     },
    #     "CNH": {
    #         "AUD": 4.77148,
    #         "CAD": 5.02831,
    #         "CHF": 6.7345,
    #         "EUR": 7.55178,
    #         "GBP": 8.7844,
    #         "HKD": 0.8569494314140522,
    #         "JPY": 0.06037046942265909,
    #         "SGD": 4.95941,
    #         "USD": 6.72668
    #     },
    #     "CZK": {
    #         "CHF": 22.8732,
    #         "EUR": 25.6481,
    #         "GBP": 29.836,
    #         "USD": 22.848
    #     },
    #     "DKK": {
    #         "CHF": 6.65741,
    #         "EUR": 7.46531,
    #         "GBP": 8.68415,
    #         "JPY": 0.05968011458582,
    #         "NOK": 0.7727497527200792,
    #         "SEK": 0.715445758479821,
    #         "USD": 6.6498
    #     },
    #     "EUR": {
    #         "AUD": 0.6318316800404372,
    #         "CAD": 0.6658543243909097,
    #         "CHF": 0.8917822267802202,
    #         "CNH": 0.13242823052046943,
    #         "CZK": 0.03900277699772224,
    #         "DKK": 0.133954525117813,
    #         "GBP": 1.1632911834161208,
    #         "HKD": 0.11347839655025674,
    #         "ILS": 0.24848424609879735,
    #         "JPY": 0.007994371962138655,
    #         "MXN": 0.04663417818919486,
    #         "NOK": 0.10350691788485684,
    #         "NZD": 0.5995599230165058,
    #         "PLN": 0.23299215515413596,
    #         "RUB": 0.013669512203457019,
    #         "SEK": 0.09583602073508145,
    #         "SGD": 0.6567368061575642,
    #         "USD": 0.8907654347380705,
    #         "ZAR": 0.06293860339239073
    #     },
    #     "GBP": {
    #         "AUD": 0.5431771517962868,
    #         "CAD": 0.5724557205500155,
    #         "CHF": 0.7666653888910185,
    #         "CNH": 0.1138472397736717,
    #         "CZK": 0.03352891869237217,
    #         "DKK": 0.11516504878967292,
    #         "EUR": 0.8597,
    #         "HKD": 0.09755726367484555,
    #         "HUF": 0.0026777346364975233,
    #         "JPY": 0.0068729467071712335,
    #         "KRW": 0.00067275,
    #         "MXN": 0.04009140841117748,
    #         "NOK": 0.08899132779510636,
    #         "NZD": 0.5154081259245133,
    #         "PLN": 0.20032051282051283,
    #         "SEK": 0.08239268352970255,
    #         "SGD": 0.5646017299397005,
    #         "USD": 0.7656733331291538,
    #         "ZAR": 0.05411079726848696
    #     },
    #     "HKD": {
    #         "AUD": 5.56788,
    #         "CNH": 1.16698,
    #         "EUR": 8.8124,
    #         "GBP": 10.25101,
    #         "JPY": 0.07045230379033394,
    #         "KRW": 0.00689701,
    #         "USD": 7.8496
    #     },
    #     "HUF": {
    #         "CHF": 286.391,
    #         "GBP": 373.601,
    #         "USD": 286.071
    #     },
    #     "ILS": {
    #         "EUR": 4.02581,
    #         "USD": 3.58581
    #     },
    #     "JPY": {
    #         "AUD": 79.037,
    #         "CAD": 83.293,
    #         "CHF": 111.552,
    #         "CNH": 16.56501,
    #         "DKK": 16.757,
    #         "EUR": 125.092,
    #         "GBP": 145.509,
    #         "HKD": 14.195,
    #         "KRW": 0.09788751,
    #         "MXN": 5.83301,
    #         "NOK": 12.9487,
    #         "NZD": 74.996,
    #         "SEK": 11.988,
    #         "SGD": 82.15,
    #         "USD": 111.425,
    #         "ZAR": 7.872
    #     },
    #     "KRW": {
    #         "CAD": 859.8452278589854,
    #         "CHF": 1151.4104778353483,
    #         "GBP": 1502.065339842283,
    #         "HKD": 146.54183256423295,
    #         "JPY": 10.322314262857732,
    #         "USD": 1144.79
    #     },
    #     "MXN": {
    #         "EUR": 21.45001,
    #         "GBP": 24.94981,
    #         "JPY": 0.1714680580728019,
    #         "USD": 19.10565
    #     },
    #     "NOK": {
    #         "CHF": 8.6159,
    #         "DKK": 1.2943,
    #         "EUR": 9.662,
    #         "GBP": 11.2394,
    #         "JPY": 0.07723802984322997,
    #         "SEK": 0.925908779467047,
    #         "USD": 8.60646
    #     },
    #     "NZD": {
    #         "AUD": 1.05388,
    #         "CAD": 1.1106668443733616,
    #         "CHF": 1.4874975828164279,
    #         "EUR": 1.66803,
    #         "GBP": 1.94039,
    #         "JPY": 0.013334577893936769,
    #         "USD": 1.485773716662952
    #     },
    #     "PLN": {
    #         "CHF": 3.8284,
    #         "EUR": 4.29301,
    #         "GBP": 4.994,
    #         "USD": 3.8241
    #     },
    #     "RUB": {
    #         "EUR": 73.39321,
    #         "USD": 65.38501
    #     },
    #     "SEK": {
    #         "CHF": 9.30631,
    #         "DKK": 1.39796,
    #         "EUR": 10.43604,
    #         "GBP": 12.1396,
    #         "JPY": 0.08343227010029393,
    #         "NOK": 1.08023,
    #         "USD": 9.29593
    #     },
    #     "SGD": {
    #         "AUD": 0.96212,
    #         "CNH": 0.2016511193653636,
    #         "EUR": 1.52276,
    #         "GBP": 1.7713,
    #         "JPY": 0.012173447276799844,
    #         "USD": 1.35639
    #     },
    #     "USD": {
    #         "AUD": 0.70932,
    #         "CAD": 0.7474958887726117,
    #         "CHF": 1.0011413010832348,
    #         "CNH": 0.14866528308843205,
    #         "CZK": 0.043784754148605456,
    #         "DKK": 0.15038317633329723,
    #         "EUR": 1.12265,
    #         "GBP": 1.30607,
    #         "HKD": 0.12739518879330003,
    #         "HUF": 0.003496748024337366,
    #         "ILS": 0.2789711543826368,
    #         "JPY": 0.008974727168294084,
    #         "KRW": 0.0008744805585482223,
    #         "MXN": 0.052350813269884146,
    #         "NOK": 0.11620475277438848,
    #         "NZD": 0.67308,
    #         "PLN": 0.26157467957101754,
    #         "RUB": 0.01533469505425415,
    #         "SEK": 0.10759051051697241,
    #         "SGD": 0.7372673921377805,
    #         "ZAR": 0.07065490027060826
    #     },
    #     "ZAR": {
    #         "AUD": 10.04151,
    #         "CHF": 14.1727,
    #         "EUR": 15.89261,
    #         "GBP": 18.4863,
    #         "JPY": 0.12706480304955528,
    #         "USD": 14.157
    #     }
    # }
    #
    # graph_volume = {
    #     "AUD": {
    #         "CAD": "1000000",
    #         "CHF": "1000000",
    #         "CNH": "1000000",
    #         "EUR": "500000",
    #         "GBP": "2000000",
    #         "HKD": "1000000",
    #         "JPY": "3000000",
    #         "KRW": "100000000",
    #         "NZD": "1000000",
    #         "SGD": "1000000",
    #         "USD": "5000000",
    #         "ZAR": "1000000"
    #     },
    #     "CAD": {
    #         "AUD": "1000000",
    #         "CHF": "1300000",
    #         "CNH": "1000000",
    #         "EUR": "2400000",
    #         "GBP": "800000",
    #         "JPY": "5500000",
    #         "NZD": "1000000",
    #         "USD": "1000000"
    #     },
    #     "CHF": {
    #         "AUD": "3000000",
    #         "CAD": "2000000",
    #         "CNH": "2000000",
    #         "CZK": "1000000",
    #         "DKK": "1000000",
    #         "EUR": "1000000",
    #         "GBP": "1000000",
    #         "HUF": "2000000",
    #         "JPY": "1000000",
    #         "KRW": "100000000",
    #         "NOK": "1000000",
    #         "NZD": "1000000",
    #         "PLN": "2000000",
    #         "SEK": "1000000",
    #         "USD": "2000000",
    #         "ZAR": "1000000"
    #     },
    #     "CNH": {
    #         "AUD": "2000000",
    #         "CAD": "1000000",
    #         "CHF": "2000000",
    #         "EUR": "2000000",
    #         "GBP": "2000000",
    #         "HKD": "1000000",
    #         "JPY": "1000000",
    #         "SGD": "1000000",
    #         "USD": "1000000"
    #     },
    #     "CZK": {
    #         "CHF": "2000000",
    #         "EUR": "1000000",
    #         "GBP": "2000000",
    #         "USD": "1000000"
    #     },
    #     "DKK": {
    #         "CHF": "1000000",
    #         "EUR": "3000000",
    #         "GBP": "1000000",
    #         "JPY": "1000000",
    #         "NOK": "14000000",
    #         "SEK": "14000000",
    #         "USD": "2000000"
    #     },
    #     "EUR": {
    #         "AUD": "600000",
    #         "CAD": "2000000",
    #         "CHF": "1000000",
    #         "CNH": "1000000",
    #         "CZK": "2000000",
    #         "DKK": "3000000",
    #         "GBP": "2000000",
    #         "HKD": "1000000",
    #         "HUF": "2000000",
    #         "ILS": "1000000",
    #         "JPY": "2000000",
    #         "KRW": "100000000",
    #         "MXN": "1000000",
    #         "NOK": "2000000",
    #         "NZD": "3600000",
    #         "PLN": "1000000",
    #         "RUB": "1000000",
    #         "SEK": "500000",
    #         "SGD": "2400000",
    #         "USD": "2000000",
    #         "ZAR": "1000000"
    #     },
    #     "GBP": {
    #         "AUD": "500000",
    #         "CAD": "1000000",
    #         "CHF": "800000",
    #         "CNH": "1000000",
    #         "CZK": "2000000",
    #         "DKK": "1900000",
    #         "EUR": "4500000",
    #         "HKD": "2000000",
    #         "HUF": "2000000",
    #         "JPY": "4000000",
    #         "MXN": "800000",
    #         "NOK": "1000000",
    #         "NZD": "500000",
    #         "PLN": "1000000",
    #         "SEK": "1000000",
    #         "SGD": "2000000",
    #         "USD": "1000000",
    #         "ZAR": "1000000"
    #     },
    #     "HKD": {
    #         "AUD": "1000000",
    #         "CNH": "3000000",
    #         "EUR": "1000000",
    #         "GBP": "800000",
    #         "JPY": "42000000",
    #         "KRW": "100000000",
    #         "USD": "2000000"
    #     },
    #     "HUF": {
    #         "CHF": "1000000",
    #         "EUR": "2000000",
    #         "GBP": "2000000",
    #         "USD": "2000000"
    #     },
    #     "ILS": {
    #         "EUR": "900000",
    #         "USD": "1000000"
    #     },
    #     "JPY": {
    #         "AUD": "1000000",
    #         "CAD": "1300000",
    #         "CHF": "1000000",
    #         "CNH": "1000000",
    #         "DKK": "33000000",
    #         "EUR": "2000000",
    #         "GBP": "800000",
    #         "HKD": "43000000",
    #         "KRW": "100000000",
    #         "MXN": "19000000",
    #         "NOK": "9000000",
    #         "NZD": "2000000",
    #         "SEK": "1000000",
    #         "SGD": "1000000",
    #         "USD": "1000000",
    #         "ZAR": "13000000"
    #     },
    #     "KRW": {
    #         "AUD": "100000000",
    #         "CHF": "100000000",
    #         "EUR": "100000000",
    #         "HKD": "100000000",
    #         "JPY": "100000000",
    #         "USD": "100000"
    #     },
    #     "MXN": {
    #         "EUR": "2000000",
    #         "GBP": "800000",
    #         "JPY": "11000000",
    #         "USD": "1000000"
    #     },
    #     "NOK": {
    #         "CHF": "1000000",
    #         "DKK": "7000000",
    #         "EUR": "1000000",
    #         "GBP": "1000000",
    #         "JPY": "8000000",
    #         "SEK": "20000000",
    #         "USD": "1000000"
    #     },
    #     "NZD": {
    #         "AUD": "1000000",
    #         "CAD": "1000000",
    #         "CHF": "2000000",
    #         "EUR": "1000000",
    #         "GBP": "1000000",
    #         "JPY": "2000000",
    #         "USD": "500000"
    #     },
    #     "PLN": {
    #         "CHF": "1000000",
    #         "EUR": "1000000",
    #         "GBP": "2900000",
    #         "USD": "1000000"
    #     },
    #     "RUB": {
    #         "EUR": "900000",
    #         "USD": "1000000"
    #     },
    #     "SEK": {
    #         "CHF": "1000000",
    #         "DKK": "1000000",
    #         "EUR": "1000000",
    #         "GBP": "900000",
    #         "JPY": "1000000",
    #         "NOK": "10000000",
    #         "USD": "1000000"
    #     },
    #     "SGD": {
    #         "AUD": "1000000",
    #         "CNH": "1000000",
    #         "EUR": "900000",
    #         "GBP": "3000000",
    #         "JPY": "500000",
    #         "USD": "1000000"
    #     },
    #     "USD": {
    #         "AUD": "1000000",
    #         "CAD": "1000000",
    #         "CHF": "1000000",
    #         "CNH": "1000000",
    #         "CZK": "2000000",
    #         "DKK": "1100000",
    #         "EUR": "9000000",
    #         "GBP": "1000000",
    #         "HKD": "1000000",
    #         "HUF": "1000000",
    #         "ILS": "1000000",
    #         "JPY": "3000000",
    #         "KRW": "100000",
    #         "MXN": "1000000",
    #         "NOK": "1100000",
    #         "NZD": "2000000",
    #         "PLN": "2100000",
    #         "RUB": "1000000",
    #         "SEK": "500000",
    #         "SGD": "4500000",
    #         "ZAR": "1000000"
    #     },
    #     "ZAR": {
    #         "AUD": "500000",
    #         "CHF": "2000000",
    #         "EUR": "500000",
    #         "GBP": "800000",
    #         "JPY": "44000000",
    #         "USD": "500000"
    #     }
    # }


    print("graph_bidprice = ")
    print(json.dumps(graph_bidprice,indent=4, sort_keys=True))


    orders = looporder(graph_bidprice,graph_volume)
    # Run for loop checking
    if len(orders) != 0:
      f = open('orders_looptest.txt','a')
      # f.write('Test message' + str(datetime.datetime.now()))
      f.write(str(datetime.datetime.now()) + '!' + json.dumps(orders) + '\n')
      f.close()
    orders = {}
    # Use inverse to calculate nodes graph_bidprice_inverse
    nested_d, nested_p = generatebellmanford(graph_bidprice_minuslog)
    print("nested_d = ")
    print(json.dumps(nested_d,indent=4, sort_keys=True))
    print("nested_p = ")
    print(json.dumps(nested_p,indent=4, sort_keys=True))
    # After generated nested bellmanford destination and predecessor json,
    # push into loop to find equivalentprices
    for cur in nested_p:
        equivalentprice = generateequivalentpricelist(nested_p[cur], cur, graph_bidprice)
        print("base = ", end='')
        print(cur)
        print("Equivalentprice List", end='')
        print(equivalentprice)
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
