import logging
from logging.handlers import TimedRotatingFileHandler
import nmap
from pprint import pprint
from Debug.Log import Timer

# ---------- log ----------
logger_script_nmap: logging.Logger = logging.getLogger(__name__)
logger_script_nmap.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger_script_nmap.addHandler(stream_handler)

# ---------- scan ----------
class Scan:
    def __init__(self, targets: list[str]) -> None:
        self.__targets: list[str] = targets
        self.__scanner: nmap.PortScanner = nmap.PortScanner()
        self.__options: str = (
            "-sS -A "  # Scan SYN + détection avancée (OS, version, scripts NSE)
            "--script smb-os-discovery "  # Script pour détecter les infos Windows via SMB
            "-O --osscan-guess "  # Détection d'OS avec estimation
            "-T4 "  # Timing agressif pour un scan rapide
            "-p 1-1024 "  # Scan des ports 1 à 1024 (ajustez cette plage si nécessaire)
            "--min-hostgroup=32 --min-parallelism=10 "  # Optimisation de la vitesse
        )

    @property
    def options(self) -> str:
        return self.__options

    @options.setter
    def options(self, options: str) -> None:
        logger_script_nmap.debug(f"New options: {options}")
        self.__options = options

    @Timer
    def scan(self) -> dict[str, dict]:
        results = {"status": "success", "data": {}}
        logger_script_nmap.debug(f"New scan request: {self.__targets}")

        try:
            for target in self.__targets:
                logger_script_nmap.debug(f"Scan Host or network: {target}")
                self.__scanner.scan(target, arguments=self.__options)
                results["data"][target] = {}

                for host in self.__scanner.all_hosts():
                    host_info = self.__scanner[host]
                    results["data"][target][host] = {
                        "hostname": host_info.hostname() or "Unknown",
                        "state": host_info.state() or "Unknown",
                        "os": "Unknown",  # Par défaut, l'OS est inconnu
                        "ports": {}
                    }

                    # Détection de l'OS
                    if "osmatch" in host_info:
                        for osmatch in host_info["osmatch"]:
                            # Prend la première correspondance d'OS
                            results["data"][target][host]["os"] = osmatch["name"]
                            break

                    # Détection des ports ouverts
                    for protocol in host_info.all_protocols():
                        results["data"][target][host]["ports"][protocol] = {}
                        for port, port_info in host_info[protocol].items():
                            results["data"][target][host]["ports"][protocol][port] = {
                                "state": port_info["state"],
                                "service": port_info["name"],  # Nom du service
                                "version": port_info["version"] if "version" in port_info else "Unknown"  # Version du service
                            }

                    # Détection des informations SMB (si disponible)
                    if "smb-os-discovery" in host_info.get("script", {}):
                        results["data"][target][host]["smb_info"] = host_info["script"]["smb-os-discovery"]

        except nmap.PortScannerError as e:
            logger_script_nmap.error(f"NMAP error: {e}")
            results["status"] = "error"
            results["message"] = str(e)
        except Exception as e:
            logger_script_nmap.error(f"Unexpected error: {e}")
            results["status"] = "error"
            results["message"] = str(e)

        return results