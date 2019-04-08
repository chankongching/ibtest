import redis
import time
import traceback
import datetime
import exec

# Run by thread
from threading import Thread
# Define redisStarter
r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance

def RedisCheck():
    try:
        p = r.pubsub()                                                              # See https://github.com/andymccurdy/redis-py/#publish--subscribe
        p.subscribe('IB')                                                 # Subscribe to startScripts channel
        PAUSE = True
        last=datetime.datetime.now()

        while PAUSE:                                                                # Will stay in loop until START message received
#            print("Waiting For redisStarter...")
            # print(str(datetime.datetime.now()))
            # print('Time difference = ' + str(datetime.datetime.now() - last))
            # last = datetime.datetime.now()
            message = p.get_message()                                               # Checks for message
            if message:
                command = message['data']                                           # Get data from message
                # print(command)
                thread = Thread(target = exec.wrapper)
                thread.start()
                # exec.wrapper()
#                if command == b'START':                                             # Checks for START message
#                    PAUSE = False                                                   # Breaks loop
            # else:
            #     print("No update on IB Channel")
            time.sleep(0.00000001)

        print("Permission to start...")

    except Exception as e:
        print("!!!!!!!!!! EXCEPTION !!!!!!!!!")
        print(str(datetime.datetime.now()) + ': ' + str(e))
        print(traceback.format_exc())


RedisCheck()
