import time
import logging
from logging.handlers import TimedRotatingFileHandler

from scapy.all import IP, ICMP, sr1
from scapy.packet import Packet

# ---------- log ----------
logger_main: logging.Logger = logging.getLogger(__name__)
logger_main.setLevel(logging.DEBUG)

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

# logger_main.addHandler(file_handler)
logger_main.addHandler(stream_handler)

# ---------- ping ----------
class Latency:
    def __init__(self, host: str, count: int = 5, timeout: int = 1, gap: int = 10):
        self.__host: str = host
        self.__count: int = count
        self.__timeout: int = timeout
        self.__gap: int = gap
    
    def ping(self) -> list[float]:
        latency = []
        for i in range(self.__count):
            packet = IP(dst=self.__host)/ICMP()
            t0: float = time.time()
            echoReply: Packet | None = sr1(packet, self.__timeout, verbose=False)
            latency.append((time.time()-t0)) # en secondes
        
        return latency
    
if __name__=="__main__":
    pck = IP(dst="8.8.8.8")/ICMP()
    t0 = time.time()
    reply = sr1(pck, timeout=5, verbose=False)
    print(f"{(time.time()-t0):.5f}")
    print(reply)