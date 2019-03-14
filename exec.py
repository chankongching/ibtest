import redis
import time
import traceback
import datetime
import json
# First approach https://gist.github.com/joninvski/701720
import bellman
# Second approach https://gist.github.com/ngenator/6178728
import bellmanford

# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance
graph_askprice = {}
graph_volume = {}

def generateGraph():
    # print("Begin table construction")
    keys = r.keys('*')
    for key in keys:
        print('key = ')
        print(key)
        print(json.loads(r.get(key)))
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
# graph_askprice sample format
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
def generatebellmanford(graph_askprice):
    ### Upgrade code by updating graph_askprice for affected node only
    nested_d = {}
    nested_p = {}
    #
    for base in graph_askprice:
        # print('generatebellmanford: run base = ' + base)
        # base = 'HKD'
        d,p = bellmanford.bellman_ford(graph_askprice, base)

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

def generateequivalentpricelist(p, base, graph_askprice):
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
            rate *= graph_askprice[p[iterator]][iterator]
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

def findtradableprice(pricelist, base, graph_askprice):
    order={}
    count=0
    for cur in pricelist:
        items = pricelist[cur]
        if items["tradetimes"] > 1: # tradetimes > 1 means there r shorter path than direct trade
            key1=items["tradestring"][:3]
            key2=items["tradestring"][-3:]
            if graph_askprice[key2].get(key1):
                if isworth(float(1/graph_askprice[key2][key1]),items["rate"]):
                    order[count] = {
                        'tradepair': key1 + ':' + key2,
                        'tradestring': tradestring,
                        'tradetimes' : tradetimes,
                        'reverseprice' : float(1/graph_askprice[key2][key1])
                        }
    return order

def isworth(reverseprice, equivalentprice):
    return reverseprice > equivalentprice

def findtradablevolume():
    print('Placeholder')
def generateorder():
    print('Placeholder')

if __name__ == '__main__':
    graph_askprice, graph_volume = generateGraph()
    # d1, p1 = bellman.bellman_ford(graph_askprice, 'HKD')
    # d2, p2 = bellmanford.bellman_ford(graph_askprice, 'HKD')
    # print('Graph Ask Price:')
    # print(json.dumps(graph_askprice,indent=4, sort_keys=True))
    # print('Graph Volume')
    # print(graph_volume)
    # print('##############################################################')
    # print('First Approach')
    # print('Distance = ')
    # print(json.dumps(d1,indent=4, sort_keys=True))
    # print('Predecessor = ')
    # print(json.dumps(p1,indent=4, sort_keys=True))
    # print('##############################################################')
    # print('Second Approach')
    # print('Distance = ')
    # print(json.dumps(d2,indent=4, sort_keys=True))
    # print('Predecessor = ')
    # print(json.dumps(p2,indent=4, sort_keys=True))
    # print('##############################################################')
    nested_d, nested_p = generatebellmanford(graph_askprice)
    # print(json.dumps(nested_p,indent=4, sort_keys=True))
    for cur in nested_p:
        if cur == 'SGD':
            equivalentprice = generateequivalentpricelist(nested_p[cur], cur, graph_askprice)
            print(json.dumps(equivalentprice,indent=4, sort_keys=True))
            print('graph_askprice = ')
            print(json.dumps(graph_askprice,indent=4, sort_keys=True))
            order = findtradableprice(equivalentprice, cur, graph_askprice)
            print('Order from ' + cur)
            print(json.dumps(order,indent=4, sort_keys=True))
