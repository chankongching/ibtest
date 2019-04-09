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

# to generate a nested destination and predecessorgraph
def generatebellmanford(graph):
    ### Upgrade code by updating graph for affected node only
    nested_d = {}
    nested_p = {}
    #
    for base in graph:
        # print('generatebellmanford: run base = ' + base)
        # base = 'HKD'
#        d,p = bellman.bellman_ford(graph,base)
        d,p = bellmanford.bellman_ford(graph, base)
        # print('d of ' + base + ' = ')
        # print(json.dumps(d,indent=4, sort_keys=True))
        # print('p of ' + base + ' = ')
        # print(json.dumps(p,indent=4, sort_keys=True))

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
    # print("base = ", end="")
    # print(json.dumps(base,indent=4, sort_keys=True))
    # print("graph = ", end="")
    # print(json.dumps(graph,indent=4, sort_keys=True))
    for cur in p:
        if (cur==base) or (not p.get(cur)):
            continue
        # print('Cur = ', end='')
        # print(cur)
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

def findtradableprice(pricelist, base, graph):
    order={}
    count=0
    for cur in pricelist:
        items = pricelist[cur]
        if items["tradetimes"] > 1: # tradetimes > 1 means there r shorter path than direct trade
            key1=items["tradestring"][:3]
            key2=items["tradestring"][-3:]
            if graph[key2].get(key1):
                # print("tradestring",end='')
                # print(items["tradestring"])
                # print("Equivalentprice = ",end='')
                # print(items["rate"])
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
    graph_bidprice, graph_bidprice_minuslog, graph_bidprice_inverse, graph_volume = generateGraph()

    orders = looporder(graph_bidprice,graph_volume)
    # Run for loop checking
    if len(orders) != 0:
        f = open('orders_loop.txt','a')
        # f.write('Test message' + str(datetime.datetime.now()))
        f.write(str(datetime.datetime.now()) + '!' + json.dumps(orders) + '\n')
        f.close()
        f = open('orders_loop_pricecheck.txt','a')
        # Print result for checking
        f.write(str("graph_bidprice = " + '\n'))
        f.write(str(json.dumps(graph_bidprice,indent=4, sort_keys=True) + '\n'))
        f.write(str("graph_bidprice_inverse = " + '\n'))
        f.write(str(json.dumps(graph_bidprice_inverse,indent=4, sort_keys=True) + '\n'))
        f.write(str("graph_bidprice_minuslog = " + '\n'))
        f.write(str(json.dumps(graph_bidprice_minuslog,indent=4, sort_keys=True) + '\n'))
        f.write(str("graph_volume = " + '\n'))
        f.write(str(json.dumps(graph_volume,indent=4, sort_keys=True) + '\n'))
        f.close()
        # sys.exit()
        os._exit(1)

    # Start BellmanFord
    orders = {}
    # Use inverse to calculate nodes graph_bidprice_inverse
    nested_d, nested_p = generatebellmanford(graph_bidprice_minuslog)
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
    # graph_bidprice, graph_bidprice_minuslog, graph_bidprice_inverse, graph_volume = generateGraph()
    # Write sample data and direct test of functions
    graph_bidprice = {
        "AUD": {
            "CAD": 0.9484,
            "CHF": 0.71203,
            "CNH": 4.78873,
            "EUR": 0.6327191739218465,
            "GBP": 0.5454436365818138,
            "HKD": 5.59219,
            "JPY": 79.468,
            "KRW": 810.8655990269613,
            "NZD": 1.05686,
            "SGD": 0.96519,
            "USD": 0.71276,
            "ZAR": 10.0358
        },
        "CAD": {
            "AUD": 1.0543407207473168,
            "CHF": 0.75076,
            "CNH": 5.04913,
            "EUR": 0.6671203084764307,
            "GBP": 0.5750960410388535,
            "JPY": 83.79,
            "NZD": 1.1142930367828132,
            "USD": 0.7514954759972344
        },
        "CHF": {
            "AUD": 1.40431687005856,
            "CAD": 1.33193036668043,
            "CNH": 6.7252,
            "CZK": 22.7633,
            "DKK": 6.63329,
            "EUR": 0.8885650562905963,
            "GBP": 0.766001777124123,
            "HUF": 285.5,
            "JPY": 111.602,
            "NOK": 8.54629,
            "NZD": 1.484185998189293,
            "PLN": 3.81069,
            "SEK": 9.26609,
            "USD": 1.0009709418135593,
            "ZAR": 14.09449
        },
        "CNH": {
            "AUD": 0.20880575635709125,
            "CAD": 0.19803862545350845,
            "CHF": 0.1486834084184546,
            "EUR": 0.13212081655949467,
            "GBP": 0.11389365976774805,
            "HKD": 1.16773,
            "JPY": 16.5941,
            "SGD": 0.20154626292919275,
            "USD": 0.14883300044352235
        },
        "CZK": {
            "CHF": 0.043918013851741565,
            "EUR": 0.03902576090477324,
            "GBP": 0.0336417157275021,
            "USD": 0.04396184112190619
        },
        "DKK": {
            "CHF": 0.15074384550564762,
            "EUR": 0.13395326906255484,
            "GBP": 0.11547344110854503,
            "JPY": 16.82399,
            "NOK": 1.2884,
            "SEK": 1.39685,
            "USD": 0.1508960205701455
        },
        "EUR": {
            "AUD": 1.58039,
            "CAD": 1.49891,
            "CHF": 1.12537,
            "CNH": 7.56829,
            "CZK": 25.6185,
            "DKK": 7.46519,
            "GBP": 0.86204,
            "HKD": 8.83819,
            "HUF": 321.3,
            "ILS": 4.03712,
            "JPY": 125.596,
            "MXN": 21.32239,
            "NOK": 9.6182,
            "NZD": 1.67026,
            "PLN": 4.2886,
            "SEK": 10.4277,
            "SGD": 1.52545,
            "USD": 1.12648,
            "ZAR": 15.86275
        },
        "GBP": {
            "AUD": 1.83325,
            "CAD": 1.7387,
            "CHF": 1.30536,
            "CNH": 8.77919,
            "CZK": 29.716,
            "DKK": 8.65923,
            "EUR": 1.1599716966906006,
            "HKD": 10.2523,
            "HUF": 372.709,
            "JPY": 145.688,
            "MXN": 24.7367,
            "NOK": 11.1569,
            "NZD": 1.9375,
            "PLN": 4.9747,
            "SEK": 12.09597,
            "SGD": 1.7695,
            "USD": 1.30669,
            "ZAR": 18.39859
        },
        "HKD": {
            "AUD": 0.17881378511232188,
            "CNH": 0.856303679536911,
            "EUR": 0.11314073009713133,
            "GBP": 0.09753433208489387,
            "JPY": 14.21,
            "USD": 0.1274538043686066
        },
        "HUF": {
            "CHF": 0.0035016457735135517,
            "EUR": 0.003111862107166307,
            "GBP": 0.002682403433476395,
            "USD": 0.0035051929433455664
        },
        "ILS": {
            "EUR": 0.24759216618386196
        },
        "JPY": {
            "AUD": 0.012583048117576002,
            "CAD": 0.011934171112145404,
            "CHF": 0.008959931187728478,
            "CNH": 0.060259114191021396,
            "DKK": 0.05943532871600077,
            "EUR": 0.007961783439490446,
            "GBP": 0.006863512196461172,
            "HKD": 0.07036802476954472,
            "KRW": 10.205070899730076,
            "MXN": 0.16976458744658782,
            "NOK": 0.07657782872755983,
            "NZD": 0.013298933425539271,
            "SEK": 0.08302324152623286,
            "SGD": 0.012145355616012437,
            "USD": 0.008968931620865322,
            "ZAR": 0.1262945188178833
        },
        "KRW": {
            "AUD": 0.0012205,
            "JPY": 0.09697949
        },
        "MXN": {
            "EUR": 0.046892877909703076,
            "GBP": 0.040419554980699664,
            "JPY": 5.88999,
            "USD": 0.05281919829964437
        },
        "NOK": {
            "CHF": 0.1169958735555397,
            "DKK": 0.7760721436664753,
            "EUR": 0.10395874916833002,
            "GBP": 0.08961697704013048,
            "JPY": 13.05749,
            "SEK": 1.08415,
            "USD": 0.11711206336231075
        },
        "NZD": {
            "AUD": 0.9461275001419192,
            "CAD": 0.89734,
            "CHF": 0.67371,
            "EUR": 0.5986482522464276,
            "GBP": 0.5160890769746858,
            "JPY": 75.19,
            "USD": 0.67438
        },
        "PLN": {
            "CHF": 0.2623632103811875,
            "EUR": 0.23314588404256312,
            "GBP": 0.20096624570937066,
            "USD": 0.26263262947788635
        },
        "RUB": {
            "USD": 0.015408515176925194
        },
        "SEK": {
            "CHF": 0.10790652705000821,
            "DKK": 0.7158247374712775,
            "EUR": 0.09588794151602671,
            "GBP": 0.08265829062654984,
            "JPY": 12.043,
            "NOK": 0.9222795060270965,
            "USD": 0.10801527335965307
        },
        "SGD": {
            "AUD": 1.03597957048287,
            "CNH": 4.96112,
            "EUR": 0.6555055914626953,
            "GBP": 0.5650994575045207,
            "JPY": 82.33,
            "USD": 0.7384160974709248
        },
        "USD": {
            "AUD": 1.4029574342714444,
            "CAD": 1.33065,
            "CHF": 0.999,
            "CNH": 6.71876,
            "CZK": 22.742,
            "DKK": 6.62699,
            "EUR": 0.8877131621230548,
            "GBP": 0.7652514616302918,
            "HKD": 7.84594,
            "HUF": 285.23,
            "JPY": 111.495,
            "MXN": 18.93129,
            "NOK": 8.53829,
            "NZD": 1.482777538885841,
            "PLN": 3.80701,
            "RUB": 64.8814,
            "SEK": 9.2571,
            "SGD": 1.35417,
            "ZAR": 14.0802
        },
        "ZAR": {
            "AUD": 0.09961201121631247,
            "CHF": 0.07093104084209331,
            "EUR": 0.06302857337345312,
            "GBP": 0.054335423435954835,
            "JPY": 7.917,
            "USD": 0.07100255609201932
        }
    }
    graph_bidprice_inverse = {
        "AUD": {
            "CAD": 1.054407423028258,
            "CHF": 1.4044352063817536,
            "CNH": 0.2088236338235816,
            "EUR": 1.58048,
            "GBP": 1.83337,
            "HKD": 0.1788208197504019,
            "JPY": 0.01258368148185433,
            "KRW": 0.00123325,
            "NZD": 0.946199118142422,
            "SGD": 1.0360654378930574,
            "USD": 1.4029968011672935,
            "ZAR": 0.09964327706809621
        },
        "CAD": {
            "AUD": 0.94846,
            "CHF": 1.3319835899621717,
            "CNH": 0.19805392216084752,
            "EUR": 1.49898,
            "GBP": 1.73884,
            "JPY": 0.011934598400763814,
            "NZD": 0.89743,
            "USD": 1.33068
        },
        "CHF": {
            "AUD": 0.71209,
            "CAD": 0.75079,
            "CNH": 0.1486944626182121,
            "CZK": 0.04393036159080625,
            "DKK": 0.15075475367427024,
            "EUR": 1.12541,
            "GBP": 1.30548,
            "HUF": 0.0035026269702276708,
            "JPY": 0.008960412895826239,
            "NOK": 0.117009837016998,
            "NZD": 0.67377,
            "PLN": 0.2624196667795071,
            "SEK": 0.10792038497359728,
            "USD": 0.99903,
            "ZAR": 0.07094971155394768
        },
        "CNH": {
            "AUD": 4.78914,
            "CAD": 5.04952,
            "CHF": 6.7257,
            "EUR": 7.56883,
            "GBP": 8.78012,
            "HKD": 0.8563623440350081,
            "JPY": 0.06026238241302631,
            "SGD": 4.96164,
            "USD": 6.71894
        },
        "CZK": {
            "CHF": 22.7697,
            "EUR": 25.6241,
            "GBP": 29.725,
            "USD": 22.747
        },
        "DKK": {
            "CHF": 6.63377,
            "EUR": 7.46529,
            "GBP": 8.66,
            "JPY": 0.05943893214392068,
            "NOK": 0.776156473144986,
            "SEK": 0.7158964813687941,
            "USD": 6.62708
        },
        "EUR": {
            "AUD": 0.6327552059934574,
            "CAD": 0.6671514633967349,
            "CHF": 0.8885966393275101,
            "CNH": 0.13213024342354746,
            "CZK": 0.03903429162519273,
            "DKK": 0.1339550634344203,
            "GBP": 1.1600389773096376,
            "HKD": 0.11314533858176842,
            "HUF": 0.003112356053532524,
            "ILS": 0.2477013316423589,
            "JPY": 0.00796203700754801,
            "MXN": 0.046899057751030725,
            "NOK": 0.10396955771350148,
            "NZD": 0.5987091830014488,
            "PLN": 0.23317632793918763,
            "SEK": 0.0958984243888873,
            "SGD": 0.6555442656265364,
            "USD": 0.8877210425395924,
            "ZAR": 0.06304077161904462
        },
        "GBP": {
            "AUD": 0.5454793399699986,
            "CAD": 0.5751423477310634,
            "CHF": 0.7660721946436232,
            "CNH": 0.11390572478782211,
            "CZK": 0.03365190469780589,
            "DKK": 0.11548370929054892,
            "EUR": 0.86209,
            "HKD": 0.09753908878983253,
            "HUF": 0.0026830583645686044,
            "JPY": 0.006863983306792599,
            "MXN": 0.04042576414800681,
            "NOK": 0.08963063216484865,
            "NZD": 0.5161290322580645,
            "PLN": 0.20101714676261884,
            "SEK": 0.08267216271204376,
            "SGD": 0.5651313930488838,
            "USD": 0.7652924565122562,
            "ZAR": 0.0543519911036661
        },
        "HKD": {
            "AUD": 5.59241,
            "CNH": 1.16781,
            "EUR": 8.83855,
            "GBP": 10.2528,
            "JPY": 0.07037297677691766,
            "USD": 7.84598
        },
        "HUF": {
            "CHF": 285.58,
            "EUR": 321.351,
            "GBP": 372.8,
            "USD": 285.291
        },
        "ILS": {
            "EUR": 4.0389
        },
        "JPY": {
            "AUD": 79.472,
            "CAD": 83.793,
            "CHF": 111.608,
            "CNH": 16.595,
            "DKK": 16.82501,
            "EUR": 125.6,
            "GBP": 145.698,
            "HKD": 14.211,
            "KRW": 0.0979905,
            "MXN": 5.89051,
            "NOK": 13.05861,
            "NZD": 75.194,
            "SEK": 12.04482,
            "SGD": 82.336,
            "USD": 111.496,
            "ZAR": 7.918
        },
        "KRW": {
            "AUD": 819.336337566571,
            "JPY": 10.31145863934735
        },
        "MXN": {
            "EUR": 21.3252,
            "GBP": 24.7405,
            "JPY": 0.169779575177547,
            "USD": 18.93251
        },
        "NOK": {
            "CHF": 8.54731,
            "DKK": 1.28854,
            "EUR": 9.6192,
            "GBP": 11.1586,
            "JPY": 0.07658439715443015,
            "SEK": 0.9223815892634784,
            "USD": 8.53883
        },
        "NZD": {
            "AUD": 1.05694,
            "CAD": 1.1144047963982437,
            "CHF": 1.4843181784447312,
            "EUR": 1.67043,
            "GBP": 1.93765,
            "JPY": 0.013299640909695438,
            "USD": 1.4828435006969365
        },
        "PLN": {
            "CHF": 3.81151,
            "EUR": 4.28916,
            "GBP": 4.97596,
            "USD": 3.8076
        },
        "RUB": {
            "USD": 64.89918
        },
        "SEK": {
            "CHF": 9.26728,
            "DKK": 1.39699,
            "EUR": 10.42884,
            "GBP": 12.098,
            "JPY": 0.0830357884248111,
            "NOK": 1.08427,
            "USD": 9.25795
        },
        "SGD": {
            "AUD": 0.96527,
            "CNH": 0.20156738800915922,
            "EUR": 1.52554,
            "GBP": 1.7696,
            "JPY": 0.012146240738491437,
            "USD": 1.35425
        },
        "USD": {
            "AUD": 0.71278,
            "CAD": 0.7515124187427197,
            "CHF": 1.001001001001001,
            "CNH": 0.14883698777750656,
            "CZK": 0.04397150646381145,
            "DKK": 0.1508980698627884,
            "EUR": 1.12649,
            "GBP": 1.30676,
            "HKD": 0.12745445415080922,
            "HUF": 0.0035059425726606595,
            "JPY": 0.008969012063321225,
            "MXN": 0.052822602157592005,
            "NOK": 0.11711947005782189,
            "NZD": 0.67441,
            "PLN": 0.2626733315646662,
            "RUB": 0.015412737702947224,
            "SEK": 0.1080251914746519,
            "SGD": 0.7384597207145336,
            "ZAR": 0.07102171844149942
        },
        "ZAR": {
            "AUD": 10.03895,
            "CHF": 14.0982,
            "EUR": 15.86582,
            "GBP": 18.4042,
            "JPY": 0.12631047113805735,
            "USD": 14.084
        }
    }
    graph_bidprice_minuslog = {
        "AUD": {
            "CAD": 0.023008454693849448,
            "CHF": 0.14750170782384453,
            "CNH": -0.6802203511758846,
            "EUR": 0.1987890044814542,
            "GBP": 0.2632501205773617,
            "HKD": -0.7475819185583987,
            "JPY": -1.9001922831075722,
            "KRW": -2.9089488758658213,
            "NZD": -0.02401746104972198,
            "SGD": 0.015387186314968354,
            "USD": 0.14705668083807003,
            "ZAR": -1.0015519978237342
        },
        "CAD": {
            "AUD": -0.022980980163390848,
            "CHF": 0.12449887435922409,
            "CNH": -0.7032165526237543,
            "EUR": 0.17579583835356086,
            "GBP": 0.24025962207519794,
            "JPY": -1.9231921904206675,
            "NZD": -0.04699941662076765,
            "USD": 0.12407362952198465
        },
        "CHF": {
            "AUD": -0.14746511305805288,
            "CAD": -0.12448152051225421,
            "CNH": -0.8277052043034158,
            "CZK": -1.3572352220420874,
            "DKK": -0.8217289845811467,
            "EUR": 0.05131076982412635,
            "GBP": 0.11577022280302923,
            "HUF": -2.455606112581867,
            "JPY": -2.0476719775870516,
            "NOK": -0.9317776255819131,
            "NZD": -0.17148833013808498,
            "PLN": -0.5810036203110347,
            "SEK": -0.9668965141181132,
            "USD": -0.00042147009350436366,
            "ZAR": -1.1490493658271344
        },
        "CNH": {
            "AUD": 0.6802575328744646,
            "CAD": 0.7032500966812326,
            "CHF": 0.8277374916954938,
            "EUR": 0.8790287508587129,
            "GBP": 0.9435004515532199,
            "HKD": -0.06734243775470763,
            "JPY": -1.2199537029252177,
            "SGD": 0.695625250124558,
            "USD": 0.8273007628660021
        },
        "CZK": {
            "CHF": 1.3573573086475157,
            "EUR": 1.4086486205263338,
            "GBP": 1.4731218632907292,
            "USD": 1.3569241276147723
        },
        "DKK": {
            "CHF": 0.8217604099838214,
            "EUR": 0.8730466831867582,
            "GBP": 0.9375178920173467,
            "JPY": -1.225929001538339,
            "NOK": -0.11005071614765377,
            "SEK": -0.14514977213429886,
            "USD": 0.8213222132874676
        },
        "EUR": {
            "AUD": -0.19876427299715912,
            "CAD": -0.1757755570131923,
            "CHF": -0.051295333593772474,
            "CNH": -0.8789977649088986,
            "CZK": -1.4085536975868913,
            "DKK": -0.8730408656312354,
            "GBP": 0.06447258176666645,
            "HKD": -0.9463633336219079,
            "HUF": -2.506910725551518,
            "ILS": -0.6060716586407524,
            "JPY": -2.098975808146478,
            "MXN": -1.3288358826077027,
            "NOK": -0.9830938035127215,
            "NZD": -0.2227840805944664,
            "PLN": -0.6323155412509909,
            "SEK": -1.0181885282290568,
            "SGD": -0.18339797724885168,
            "USD": -0.05172348548129294,
            "ZAR": -1.2003784797215098
        },
        "GBP": {
            "AUD": -0.26322169366764814,
            "CAD": -0.24022465412227756,
            "CHF": -0.11573030052677714,
            "CNH": -0.9434544481660085,
            "CZK": -1.472990349676658,
            "DKK": -0.9374792752022474,
            "EUR": -0.06444739257083867,
            "HKD": -1.0108213059045514,
            "HUF": -2.5713698800174423,
            "JPY": -2.163423781362247,
            "MXN": -1.3933417620925284,
            "NOK": -1.047543540487184,
            "NZD": -0.2872417111783479,
            "PLN": -0.6967668956801321,
            "SEK": -1.0826407010365449,
            "SGD": -0.2478505669735337,
            "USD": -0.11617256749015764,
            "ZAR": -1.2647845415593622
        },
        "HKD": {
            "AUD": 0.7475990036192915,
            "CNH": 0.06737218981081959,
            "EUR": 0.9463810230842755,
            "GBP": 1.010842485732106,
            "JPY": -1.1525940779274697,
            "USD": 0.8946471967452494
        },
        "HUF": {
            "CHF": 2.455727789260369,
            "EUR": 2.5069796557130632,
            "GBP": 2.571475903681944,
            "USD": 2.4552880712995964
        },
        "ILS": {
            "EUR": 0.6062631005119478
        },
        "JPY": {
            "AUD": 1.900214142651148,
            "CAD": 1.923207739532998,
            "CHF": 2.047695325706688,
            "CNH": 1.2199772567446228,
            "DKK": 1.225955331020444,
            "EUR": 2.0989896394011773,
            "GBP": 2.1634535902399605,
            "HKD": 1.1526246394476192,
            "KRW": -1.0088160263234836,
            "MXN": 0.7701528976049608,
            "NOK": 1.1158969517126425,
            "NZD": 1.8761831880537378,
            "SEK": 1.0808003142064373,
            "SGD": 1.9155897645302526,
            "USD": 2.04725928703361,
            "ZAR": 0.8986154974161858
        },
        "KRW": {
            "AUD": 2.9134622162467925,
            "JPY": 1.0133201041013786
        },
        "MXN": {
            "EUR": 1.3288931129222838,
            "GBP": 1.3934084723766382,
            "JPY": -0.7701145574444012,
            "USD": 1.2772081948875746
        },
        "NOK": {
            "CHF": 0.9318294555500961,
            "DKK": 0.11009790485016627,
            "EUR": 0.9831389545707953,
            "GBP": 1.0476097097973642,
            "JPY": -1.1158597019073477,
            "SEK": -0.035089374144705504,
            "USD": 0.9313983672517531
        },
        "NZD": {
            "AUD": 0.024050334130021795,
            "CAD": 0.047042972623379704,
            "CHF": 0.1715270062875364,
            "EUR": 0.22282828108118455,
            "GBP": 0.28727533267548644,
            "JPY": -1.8761600848256281,
            "USD": 0.17109531800732794
        },
        "PLN": {
            "CHF": 0.5810970635364906,
            "EUR": 0.6323722471765966,
            "GBP": 0.6968768805555318,
            "USD": 0.580651318148037
        },
        "RUB": {
            "USD": 1.81223920953188
        },
        "SEK": {
            "CHF": 0.9669522849179379,
            "DKK": 0.14519329733797365,
            "EUR": 1.0182360045324,
            "GBP": 1.082713580171332,
            "JPY": -1.080734686353143,
            "NOK": 0.03513744171268739,
            "USD": 0.9665148309312666
        },
        "SGD": {
            "AUD": -0.01535119120647383,
            "CNH": -0.6955797319157538,
            "EUR": 0.1834235994261663,
            "GBP": 0.2478751096246043,
            "JPY": -1.9155581154115204,
            "USD": 0.13169884425924033
        },
        "USD": {
            "AUD": -0.14704449473366238,
            "CAD": -0.12406383830146137,
            "CHF": 0.0004345117740176917,
            "CNH": -0.8272891279870054,
            "CZK": -1.356828655196462,
            "DKK": -0.8213163152496011,
            "EUR": 0.05172734078768323,
            "GBP": 0.11619583222737509,
            "HKD": -0.894644982640248,
            "HUF": -2.4551952019275767,
            "JPY": -2.0472553918586307,
            "MXN": -1.277180208300486,
            "NOK": -0.9313709013769093,
            "NZD": -0.17107599871454074,
            "PLN": -0.5805840175916499,
            "RUB": -1.812120212437915,
            "SEK": -0.9664749552290808,
            "SGD": -0.13167318829852348,
            "ZAR": -1.148608823717989
        },
        "ZAR": {
            "AUD": 1.0016882911901992,
            "CHF": 1.1491636672674836,
            "EUR": 1.2004625228450168,
            "GBP": 1.2649169441333163,
            "JPY": -0.8985606449397121,
            "USD": 1.1487260163981465
        }
    }
    graph_volume = {
        "AUD": {
            "CAD": "1000000",
            "CHF": "3000000",
            "CNH": "1000000",
            "EUR": "2000000",
            "GBP": "500000",
            "HKD": "2000000",
            "JPY": "2000000",
            "KRW": "100000000",
            "NZD": "2000000",
            "SGD": "1000000",
            "USD": "1000000",
            "ZAR": "500000"
        },
        "CAD": {
            "AUD": "1000000",
            "CHF": "1000000",
            "CNH": "1000000",
            "EUR": "1000000",
            "GBP": "800000",
            "JPY": "1000000",
            "NZD": "1000000",
            "USD": "1000000"
        },
        "CHF": {
            "AUD": "1000000",
            "CAD": "1300000",
            "CNH": "1000000",
            "CZK": "2000000",
            "DKK": "1000000",
            "EUR": "2000000",
            "GBP": "800000",
            "HUF": "1000000",
            "JPY": "2000000",
            "NOK": "1000000",
            "NZD": "1000000",
            "PLN": "2000000",
            "SEK": "1000000",
            "USD": "1000000",
            "ZAR": "1000000"
        },
        "CNH": {
            "AUD": "1000000",
            "CAD": "2000000",
            "CHF": "3000000",
            "EUR": "1000000",
            "GBP": "1000000",
            "HKD": "1000000",
            "JPY": "1000000",
            "SGD": "1000000",
            "USD": "1000000"
        },
        "CZK": {
            "CHF": "1000000",
            "EUR": "2000000",
            "GBP": "1000000",
            "USD": "1000000"
        },
        "DKK": {
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "900000",
            "JPY": "32000000",
            "NOK": "14000000",
            "SEK": "7000000",
            "USD": "1100000"
        },
        "EUR": {
            "AUD": "1600000",
            "CAD": "900000",
            "CHF": "1000000",
            "CNH": "2000000",
            "CZK": "2000000",
            "DKK": "1000000",
            "GBP": "4000000",
            "HKD": "1000000",
            "HUF": "2000000",
            "ILS": "1000000",
            "JPY": "2000000",
            "MXN": "1000000",
            "NOK": "1000000",
            "NZD": "1000000",
            "PLN": "1000000",
            "SEK": "1000000",
            "SGD": "1000000",
            "USD": "2000000",
            "ZAR": "20000"
        },
        "GBP": {
            "AUD": "500000",
            "CAD": "500000",
            "CHF": "1000000",
            "CNH": "765000",
            "CZK": "1000000",
            "DKK": "2000000",
            "EUR": "500000",
            "HKD": "2000000",
            "HUF": "2000000",
            "JPY": "2500000",
            "MXN": "800000",
            "NOK": "1000000",
            "NZD": "1200000",
            "PLN": "1000000",
            "SEK": "1000000",
            "SGD": "2000000",
            "USD": "400000",
            "ZAR": "800000"
        },
        "HKD": {
            "AUD": "1000000",
            "CNH": "7000000",
            "EUR": "2000000",
            "GBP": "2000000",
            "JPY": "31000000",
            "USD": "1000000"
        },
        "HUF": {
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "900000",
            "USD": "2100000"
        },
        "ILS": {
            "EUR": "900000"
        },
        "JPY": {
            "AUD": "1000000",
            "CAD": "3800000",
            "CHF": "1000000",
            "CNH": "7000000",
            "DKK": "47000000",
            "EUR": "1000000",
            "GBP": "800000",
            "HKD": "29000000",
            "KRW": "100000000",
            "MXN": "19000000",
            "NOK": "8000000",
            "NZD": "1500000",
            "SEK": "9000000",
            "SGD": "3500000",
            "USD": "1000000",
            "ZAR": "26000000"
        },
        "KRW": {
            "AUD": "100000000",
            "JPY": "100000000"
        },
        "MXN": {
            "EUR": "900000",
            "GBP": "800000",
            "JPY": "1000000",
            "USD": "1000000"
        },
        "NOK": {
            "CHF": "1000000",
            "DKK": "7000000",
            "EUR": "1000000",
            "GBP": "900000",
            "JPY": "9000000",
            "SEK": "10000000",
            "USD": "1100000"
        },
        "NZD": {
            "AUD": "2900000",
            "CAD": "2000000",
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "500000",
            "JPY": "5000000",
            "USD": "2000000"
        },
        "PLN": {
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "1000000",
            "USD": "2500000"
        },
        "RUB": {
            "USD": "1000000"
        },
        "SEK": {
            "CHF": "1000000",
            "DKK": "1000000",
            "EUR": "1000000",
            "GBP": "900000",
            "JPY": "1000000",
            "NOK": "1000000",
            "USD": "1000000"
        },
        "SGD": {
            "AUD": "1000000",
            "CNH": "2000000",
            "EUR": "1000000",
            "GBP": "800000",
            "JPY": "1000000",
            "USD": "2500000"
        },
        "USD": {
            "AUD": "2000000",
            "CAD": "3348890",
            "CHF": "1000000",
            "CNH": "1000000",
            "CZK": "1000000",
            "DKK": "2200000",
            "EUR": "2500000",
            "GBP": "4000000",
            "HKD": "25000",
            "HUF": "1000000",
            "JPY": "1000000",
            "MXN": "1000000",
            "NOK": "500000",
            "NZD": "1000000",
            "PLN": "1000000",
            "RUB": "1000000",
            "SEK": "1100000",
            "SGD": "1000000",
            "ZAR": "500000"
        },
        "ZAR": {
            "AUD": "1000000",
            "CHF": "1000000",
            "EUR": "1000000",
            "GBP": "800000",
            "JPY": "13000000",
            "USD": "1000000"
        }
    }


    # print("graph_bidprice = ")
    # print(json.dumps(graph_bidprice,indent=4, sort_keys=True))


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
    # print("nested_d = ")
    # print(json.dumps(nested_d,indent=4, sort_keys=True))
    # print("nested_p = ")
    # print(json.dumps(nested_p,indent=4, sort_keys=True))
    # After generated nested bellmanford destination and predecessor json,
    # push into loop to find equivalentprices
    for cur in nested_p:
        equivalentprice = generateequivalentpricelist(nested_p[cur], cur, graph_bidprice)
        # print("base = ", end='')
        # print(cur)
        # print("Equivalentprice List", end='')
        # print(equivalentprice)
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
