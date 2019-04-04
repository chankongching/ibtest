import io
import json

filepath = 'orders.process.txt'
with open(filepath) as fp:
    line = fp.readline()
    cnt = 1
    while line:
#        print(line.strip())
        print("Line :{}:{}:{}".format(cnt, line.strip()))
        line = fp.readline()
        cnt += 1
        if cnt== 10:
            break
#file_paprint(line.strip())th = './orders.process.txt'
#with open(file_path) as f:
#    for line in f:
#        j_content = json.loads(line)
#        print(j_content)
#        break

#filepath = './orders.process.txt'
#data = []
#with open(filepath) as f:
#    for line in f:
#        print(line)
#        data.append(json.loads(line))
#        break

#print('Data = ')
#print(data)

# fp = open('orders.txt', 'r')

#filepath = 'orders.process.txt'
#with open(filepath) as fp:
#   line = fp.readline()
#   cnt = 1
#   while line:
#       # line.strip().split('!')[1]
#       print(line.strip())
#       print("{}:{}".format(cnt, line.strip()))
#       line = fp.readline()
#       cnt += 1
#       break
