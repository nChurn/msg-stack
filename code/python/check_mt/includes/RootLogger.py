import logging

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

mylogHandler = logging.StreamHandler()
mylogFormatter = logging.Formatter(
    # fmt='[%(asctime)s](%(name)s)%(levelname)s: %(message)s',
    fmt='[%(asctime)s]%(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
mylogHandler.setFormatter(mylogFormatter)
mylogHandler.setLevel(logging.INFO)

rootLogger.addHandler(mylogHandler)
