import redis
import time
import traceback
import datetime

def RedisCheck():
    try:
        r = redis.StrictRedis(host='localhost', port=6379)                          # Connect to local Redis instance

        p = r.pubsub()                                                              # See https://github.com/andymccurdy/redis-py/#publish--subscribe
        p.subscribe('IB')                                                 # Subscribe to startScripts channel
        PAUSE = True

        while PAUSE:                                                                # Will stay in loop until START message received
#            print("Waiting For redisStarter...")
            print(str(datetime.datetime.now()))
            message = p.get_message()                                               # Checks for message
            if message:
                command = message['data']                                           # Get data from message
                print(command)
#                if command == b'START':                                             # Checks for START message
#                    PAUSE = False                                                   # Breaks loop
            else:
                print("No update on IB Channel")
            time.sleep(1)

        print("Permission to start...")

    except Exception as e:
        print("!!!!!!!!!! EXCEPTION !!!!!!!!!")
        print(str(e))
        print(traceback.format_exc())


RedisCheck()
