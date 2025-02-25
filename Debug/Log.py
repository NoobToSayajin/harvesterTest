import datetime, logging, time
from logging.handlers import TimedRotatingFileHandler

logLevel: dict = {
    "DEBUG":logging.DEBUG,
    "INFO":logging.INFO,
    "WARNING":logging.WARNING,
    "ERROR":logging.ERROR,
    "CRITICAL":logging.CRITICAL
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formater = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

# file_handler = TimedRotatingFileHandler(
#     filename="..\\tmp\\.log", # type: ignore
#     when='H',
#     interval=24,
#     backupCount=5,
#     encoding='utf-8'
# )

# file_handler.setFormatter(formater)
# file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formater)

# logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def Timer(func):
    """
    :decorator: retourne le temps d execution de la fonction obsevee.
    """
    def wrapper(*args, **kwargs):
        msg: str = f"Debut de {func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        t1 = datetime.datetime.now()
        res = func(*args, **kwargs)
        t2 = datetime.datetime.now() - t1
        msg = f"Arret de{func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        logger.info(f'Fonction {func.__name__!r} executee en {(t2)}s')
        return res
    return wrapper
