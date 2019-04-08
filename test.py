# For testing purpose
import os
import datetime
import sys
import json

orders = {}

f = open('orders_test.txt','a')
# f.write('Test message' + str(datetime.datetime.now()))
f.write(str(datetime.datetime.now()) + '!' + json.dumps(orders) + '\n')
f.close()
