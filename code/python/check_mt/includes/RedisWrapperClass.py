import redis
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

class RedisWrapperClass(redis.Redis):
    """Redis client wrapper to have 'with' sougar"""

    host = os.getenv('REDIS_HOST')
    port = int(os.getenv('REDIS_PORT'))
    password = os.getenv('REDIS_PASSWORD') if os.getenv('REDIS_PASSWORD') != 'null' else None
    decode_responses = True if os.getenv('REDIS_DECODERESPONSES') == 'True' else False

    def __init__(self, *args, **kwargs):
        # fill with default values
        if "host" not in kwargs:
            kwargs["host"] = self.host

        if "port" not in kwargs:
            kwargs["port"] = self.port

        if "password" not in kwargs and self.password is not None:
            kwargs["password"] = self.password

        if "decode_responses" not in kwargs:
            kwargs["decode_responses"] = self.decode_responses

        super().__init__(*args, **kwargs)


    def __enter__(self):
        return self

    # def __exit__(self, type, value, traceback):
    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)
        # pass
