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

from pathlib import Path

if __name__ == "__main__":
    start_time = time.time()
    rootLogger.info("Begin")

    rootLogger.info(f"__file__ is:{__file__}")
    rootLogger.info(f"dirname(__file__) is:{dirname(__file__)}")

    dir_path = join(dirname(__file__), '../attachements')
    Path(f"{dir_path}").mkdir(parents=True, exist_ok=True)
