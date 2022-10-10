import socket, requests, time, datetime, threading
import concurrent.futures

from includes.RootLogger import rootLogger

import os
from os.path import join, dirname
from dotenv import load_dotenv
import redis
from random import randint
# print(randint(0, 9))

# Create .env file path.
# dotenv_path = "/app/includes/.env"
dotenv_path = join(dirname(__file__), 'includes/.env')
# Load file from the path.
load_dotenv(dotenv_path)
# create redis instance
env_host = os.getenv('REDIS_HOST')
env_port = int(os.getenv('REDIS_PORT'))
env_password = os.getenv('REDIS_PASSWORD') if os.getenv('REDIS_PASSWORD') != 'null' else None
env_decode_responses = True if os.getenv('REDIS_DECODERESPONSES') == 'True' else False
env_max_connections = int(os.getenv('REDIS_MAX_CONN', default=4096))

# Use a thread-safe blocking connection pool.
redis_conn_pool = redis.BlockingConnectionPool(
    host=env_host,
    port=env_port,
    max_connections=env_max_connections,
    decode_responses=env_decode_responses,
    timeout=300,
)

class TestThread(threading.Thread):
    def __init__(self, my_redis=None, threadLock=None, thread_id=0):
        self.thread_id = thread_id
        self.my_redis = my_redis
        self.threadLock = threadLock
        # start regular
        threading.Thread.__init__(self)

    def run(self):
        socks_list = my_redis.smembers('socks:smtp')

        for record in socks_list:
            sock = my_redis.hgetall(record)
            # if sock:
            #     rootLogger.info(f"Thread[{self.thread_id}]: Found real socket")
            # else:
            #     rootLogger.info(f"Thread[{self.thread_id}]: Found dead record")

            # imitate some work
            time.sleep(randint(2, 7))


threads = []
threadLock = threading.Lock()

if __name__ == "__main__":
    start_time = time.time()
    rootLogger.info("Begin")

    # create redis instance to share among all futher processes
    my_redis = redis.Redis(connection_pool=redis_conn_pool, decode_responses=env_decode_responses)
    # create dummy redis variant
    # my_redis = redis.Redis(host=env_host, env_port=env_port, decode_responses=env_decode_responses)

    for x in range(0, 100000):
        new_thread = TestThread(my_redis=my_redis, threadLock=threadLock, thread_id=x)
        new_thread.daemon = True
        new_thread.start()
        threads.append(new_thread)

    rootLogger.info("Done adding threads")


    while True:
        # for thread in threads:
        #     if not thread.isAlive():

        done_threads = [thread for thread in threads if not thread.isAlive()]
        live_threads = [thread for thread in threads if thread.isAlive()]

        rootLogger.info(f"Done threads:{[thread.thread_id for thread in done_threads]}")

        threads = live_threads

        if len(threads) < 1:
            break

        time.sleep(0.05)


    rootLogger.info("End")
    end_time = time.time()
    time_delta = end_time - start_time
    rootLogger.info(f"All processes are finnished, processing done in {datetime.timedelta(seconds=time_delta)}")


