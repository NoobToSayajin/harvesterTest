import re
import logging
import json
import requests
import os
import queue
import threading
from logging.handlers import TimedRotatingFileHandler
import pprint

import customtkinter as ctk
from PIL import ImageFont

import Scripts.Script_nmap
import Debug.Log

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

# ---------- App ----------
URL: str = "192.168.1.1"
JSON_FILE: str = "Export\\scan.json"
resultQueue = queue.Queue()

def getVersion() -> str:
    with open("version", "r") as file:
        return file.read()

def startScan(targets: list[str]) -> dict[str, dict]:
    # ma fonction très longue en durée
    scanner = Scripts.Script_nmap.Scan(targets)
    result: dict[str, dict] = scanner.scan()
    timer = getattr(scanner.scan, 'Debug.Log.Timer', None)
    return result, timer

def sendToServer(file, url):
    if not os.path.exists(file):
        logger_main.debug(f"Fichier {file} introuvable.")
    with open(file, "r"):
        data = json.load(file)
    response: requests.Response = requests.post(url=url, json=file)#, data=data)
    logger_main.debug(f"Réponse du serveur: {response.status_code} - {response.text}")

def scanToJson(data: dict):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def checkTargetNet(void = None) -> bool:
    IP_REGEX = r"^(\d{1,3}\.){3}\d{1,3}$"
    NETWORK_REGEX = r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$"

    def validIP(ip: str) -> bool:
        octets: list[str] = ip.split(".")
        logger_main.debug(f"validIP: {all(0 <= int(octet) <= 255 for octet in octets)}")
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    def validNetwork(networks: str) -> bool:
        ip, mask = networks.split("/")
        mask = int(mask)
        return validIP(ip) and (0 <= mask < 32)
    
    targetNetInput: str = targetNetEntry.get().strip()
    
    if re.match(NETWORK_REGEX, targetNetInput) and validNetwork(targetNetInput) or re.match(IP_REGEX, targetNetInput) and validIP(targetNetInput):
        logger_main.debug(f"Lancement du scan: {targetNetInput}")
        global txtBoxResult
        if txtBoxResult is not None:
            txtBoxResult.destroy()
        
        targetNetEntry.configure(border_color="gray")
        labelResult.configure(text="Lancement du scan", bg_color="green")
        targetNetBtn.configure(state="disabled")
        targetHostBtn.configure(state="disabled")
        targetNetEntry.configure(state="disabled")
        targetHostEntry.configure(state="disabled")
                
        labelResult.configure(text="Scan en cours ...", bg_color="#fe6807")
        thread = threading.Thread(
            target=lambda: resultQueue.put(startScan([targetNetInput])),
            daemon=True
        )
        thread.start()
        # Vérifie régulièrement si le résultat est prêt
        def check_result():
            try:
                resultat, timer = resultQueue.get_nowait()  # Récupère les données sans bloquer
                scanToJson(resultat)
                sendToServer(JSON_FILE, URL)
                logger_main.debug(f"Résultat du scan : {pprint.pformat(resultat)}")
                
                labelResult.configure(text=f"Scan terminé en: {timer}", bg_color=color1)
                targetNetBtn.configure(state="normal")
                targetHostBtn.configure(state="normal")
                targetNetEntry.configure(state="normal")
                targetHostEntry.configure(state="normal")

                global txtBoxResult
                txtBoxResult = ctk.CTkTextbox(tabScan1)
                txtBoxResult.grid(row=3, columnspan=4, sticky="nsew", padx=10, pady=10)
                txtBoxResult.insert("1.0", f"{pprint.pformat(resultat, 4)}")
                # labelResult.configure(text=f"Scan terminé : {pprint.pformat(resultat)}", bg_color=color1)
            except queue.Empty:
                targetNetEntry.after(100, check_result)  # Continue à vérifier toutes les 100ms

        check_result()  # Lance la vérification immédiate
        # labelResult.configure(text="", bg_color="transparent")
    else:
        targetNetEntry.configure(border_color="red")
        labelResult.configure(text="❌ Adresse invalide", bg_color="red")

def checkTargetHost(void = None) -> bool:
    HOSTNAME_REGEX = r"^[a-zA-Z0-9.-]+$"

    targetHostInput: str = targetHostEntry.get().strip()
    
    if re.match(HOSTNAME_REGEX, targetHostInput):
        labelResult.configure(text="Lancement du scan", bg_color="green")
        targetHostEntry.configure(border_color="gray")
    else:
        targetHostEntry.configure(border_color="red")
        labelResult.configure(text="❌ Nom d'hôte invalide", bg_color="red")

def onClick(btn: ctk.CTkButton):
    pass

def onHoverIn(btn: ctk.CTkButton) -> None:
    btn.configure(text_color=color2, fg_color=color3)

def onHoverOut(btn: ctk.CTkButton) -> None:
    btn.configure(text_color=color3, fg_color=color2)

# ---------- init ----------

root = ctk.CTk()
screen_width: int = root.winfo_screenwidth()
screen_height: int = root.winfo_screenheight()

color0: str = "white"
color1: str = "#191bdf" # bleu
color2: str = "#09080d" # noir
color3: str = "#fe6807" # orange

# root.geometry(f"{screen_width}x{screen_height}+0+0")
root.geometry("1000x600")
# root.attributes("-fullscreen", True)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("Ressources\\Themes\\orange.json")
baseFontSize: int = 16

try:
    _monserratBlack: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Montserrat\\static\\Montserrat-ExtraBoldItalic.ttf", 2*baseFontSize)
    _loraItalic: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Lora\\static\\Lora-Italic.ttf", baseFontSize)
    _hindMadurai: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Hind_Madurai\\HindMadurai-Regular.ttf", baseFontSize)
except IOError as e:
    print(f"Error loading font: {e}")

monserratBlack = ctk.CTkFont(family=_monserratBlack.getname()[0], size=baseFontSize, weight="bold")
loraItalic = ctk.CTkFont(family=_loraItalic.getname()[0], size=baseFontSize, slant="italic")
hindMadurai = ctk.CTkFont(family=_hindMadurai.getname()[0], size=baseFontSize)

root.option_add("*Font", hindMadurai)
root.title("Harvester")

# btnLst: list[ctk.CTkButton] = []

menuWidth: int = 350
bntY: int = 50

# ---------- menu ----------

menu = ctk.CTkFrame(root, width=menuWidth, height=30, fg_color=color1, corner_radius=0)
menu.pack(side="left", fill="y")

appName = ctk.CTkLabel(menu, width=menuWidth, height=bntY, text="Harvester", text_color=color0, font=monserratBlack, bg_color=color1)
appName.pack(fill="x")

scanBtn = ctk.CTkButton(menu, width=menuWidth, height=bntY, text="nmap", corner_radius=0)
scanBtn.pack(fill="x")

# btnLst.append(scanBtn)
scanBtn.bind("<Enter>", lambda e: onHoverIn(scanBtn))
scanBtn.bind("<Leave>", lambda e: onHoverOut(scanBtn))

version = ctk.CTkLabel(menu, width=menuWidth, height=bntY/2, text=getVersion(), text_color=color0, font=loraItalic, bg_color=color1)
version.pack(fill="x", side="bottom")

version = ctk.CTkLabel(menu, width=menuWidth, height=bntY/2, text="Version", text_color=color0, font=monserratBlack, bg_color=color1)
version.pack(fill="x", side="bottom")

quitBtn = ctk.CTkButton(menu, width=menuWidth, height=bntY, text="Quitter", corner_radius=0, command=root.destroy)
quitBtn.pack(fill="x", side="bottom")
# btnLst.append(quitBtn)
quitBtn.bind("<Enter>", lambda e: onHoverIn(quitBtn))
quitBtn.bind("<Leave>", lambda e: onHoverOut(quitBtn))

# ---------- tab ----------
txtBoxResult: ctk.CTkTextbox = None
tabScan = ctk.CTkTabview(root)
tabScan.pack(expand=True, fill="both", anchor="w")

tabScan1: ctk.CTkFrame = tabScan.add("Scan")
tabScan2: ctk.CTkFrame = tabScan.add("Result")

for col in range(4):
    tabScan1.grid_columnconfigure(col, weight=1, uniform="equal")

targetNetLabel = ctk.CTkLabel(tabScan1, text="Réseaux à scanner: ")
targetNetLabel.grid(row=0, column=0, pady=10, padx=5, sticky="e")

targetNetEntry = ctk.CTkEntry(tabScan1, placeholder_text="0.0.0.0/0", placeholder_text_color="gray")
targetNetEntry.grid(row=0, column=1, pady=10, padx=5, sticky="w")
targetNetEntry.bind("<Return>", checkTargetNet)

targetNetBtn = ctk.CTkButton(tabScan1, text="Lancer le scan NMAP", command=checkTargetNet)
targetNetBtn.grid(row=1, column=0, columnspan=2, pady=10, padx=5)
targetNetBtn.bind("<Enter>", lambda e: onHoverIn(targetNetBtn))
targetNetBtn.bind("<Leave>", lambda e: onHoverOut(targetNetBtn))

targetHostLabel = ctk.CTkLabel(tabScan1, text="Nom d'hôte à scanner: ")
targetHostLabel.grid(row=0, column=2, pady=10, padx=5, sticky="e")

targetHostEntry = ctk.CTkEntry(tabScan1, placeholder_text="host.lan", placeholder_text_color="gray")
targetHostEntry.grid(row=0, column=3, pady=10, padx=5, sticky="w")
targetHostEntry.bind("<Return>", checkTargetHost)

targetHostBtn = ctk.CTkButton(tabScan1, text="Lancer le scan NMAP", command=checkTargetHost)
targetHostBtn.grid(row=1, column=2, columnspan=2, pady=10, padx=5)
targetHostBtn.bind("<Enter>", lambda e: onHoverIn(targetHostBtn))
targetHostBtn.bind("<Leave>", lambda e: onHoverOut(targetHostBtn))

labelResult = ctk.CTkLabel(tabScan1, text="")
labelResult.grid(row=2, columnspan=4)


# for i, btn in enumerate(btnLst):
#     btn.bind("<Enter>", lambda e: onHoverIn(btn))
#     btn.bind("<Leave>", lambda e: onHoverOut(btn))

# ---------- loop ----------

root.mainloop()