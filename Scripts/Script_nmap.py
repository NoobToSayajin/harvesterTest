import logging
from logging.handlers import TimedRotatingFileHandler

import nmap
from pprint import pprint

from Debug.Log import Timer

# ---------- log ----------
logger_script_nmap: logging.Logger = logging.getLogger(__name__)
logger_script_nmap.setLevel(logging.DEBUG)

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

# logger_script_nmap.addHandler(file_handler)
logger_script_nmap.addHandler(stream_handler)

# ---------- scan ----------
class Scan:
    def __init__(self, targets: list[str]) -> None:
        self.__targets: list[str] = targets
        self.__scanner: nmap.PortScanner = nmap.PortScanner()
        self.__result: dict[str, dict[str, dict[str, dict[int, str]]]] = {}
        self.__options: str = "-sS -sV -O -A"
    
    @property
    def options(self) -> str:
        """
        -sS: TCP SYN scan  
        -sV: version detection  
        -O: OS detection  
        -A: aggressive scan  
        -p: scan ports/port range 
        """
        return self.__options
    
    @options.setter
    def options(self, options) -> None:
        logger_script_nmap.debug(f"New options: {options}")
        self.__options = options
    @Timer
    def scan(self) -> dict[str, dict]:
        logger_script_nmap.debug(f"New scan request: {self.__targets}")
        try:
            for target in self.__targets:
                logger_script_nmap.debug(f"Scan Host or network: {target}")
                self.__result[target] = {}
                self.__scanner.scan(target, arguments=self.__options)
                for host in self.__scanner.all_hosts():
                    self.__result[target][host] = {}
                    if self.__scanner[host].get("osmatch") != []:
                        for os in self.__scanner[host].get("osmatch")[0]['osclass']:
                            self.__result[target][host]['OSfamily'] = os['osfamily']
                            self.__result[target][host]['OSgen'] = os['osgen']
                            self.__result[target][host]['type'] = os['type']
                            self.__result[target][host]['vendor'] = os['vendor']
                        self.__result[target][host]['hostname'] = self.__scanner[host].hostname()
                        self.__result[target][host]['VMname'] = self.__scanner[host].get("hostnames", ['Inconnu'][0])
                        self.__result[target][host]['state'] = self.__scanner[host].state()
                        self.__result[target][host]['OSname'] = self.__scanner[host].get("osmatch")[0]['name']
                        self.__result[target][host]['protocol'] = {}
                        for __protocol in self.__scanner[host].all_protocols():
                            self.__result[target][host]['protocol'][__protocol] = {}
                            for __port in self.__scanner[host][__protocol].keys():
                                self.__result[target][host]['protocol'][__protocol][__port] = self.__scanner[host][__protocol][__port]['state']
        except nmap.PortScannerError as e:
            print(f"NMAP à rencontré une erreur: {e}")
        except Exception as e:
            print(e)
        finally:
            logger_script_nmap.debug(f"Scan end")
            return self.__result

if __name__ == "__main__":
    scan = Scan(["Bbox-TV-001.lan"])
    pprint(scan.scan())
