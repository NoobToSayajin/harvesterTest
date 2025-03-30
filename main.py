# Python included libraries
import re
import logging
import json
import os
import queue
import threading
from logging.handlers import TimedRotatingFileHandler
import pprint
import datetime

# PIP libraries
import requests
import customtkinter as ctk
from PIL import ImageFont

# Custom libraries
import Scripts.Script_nmap
import Scripts.Latency
import Debug.Log

# -------------------- log --------------------

logger_main: logging.Logger = logging.getLogger(__name__)
logger_main.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger_main.addHandler(stream_handler)

# -------------------- App --------------------

URL: str = "http://172.16.2.253:5000/api/data"  # URL du serveur Nester
resultQueue = queue.Queue()
HOST: str = "172.16.2.254" # Router Simulant Internet
HOST2: str = "www.google.com"
latency = Scripts.Latency.Latency(HOST)
latencyGoogle = Scripts.Latency.Latency("google.com")
previousLabel: list[ctk.CTkLabel] = []

def getVersion() -> str:
    """Récupère la version de l'application depuis le fichier VERSION."""
    with open("VERSION", "r") as file:
        return file.read()

def getLatency() -> float:
    """Met à jour la latence affichée dans l'interface graphique."""
    global latency
    global labelLatency
    ping_result = latency.ping()
    if ping_result != -1:
        labelLatency.configure(text=f"Latence vers Datacenter {HOST:>15}: {ping_result:9.3f} ms")
    else:
        labelLatency.configure(text=f"Latence vers Datacenter {HOST:>15}:   Erreur")
    root.after(1000, getLatency)  # Mettre à jour la latence toutes les secondes

def getLatencyGoogle() -> float:
    """Met à jour la latence affichée dans l'interface graphique."""
    global latencyGoogle
    global labelLatencyGoogle
    ping_result = latency.ping()
    if ping_result != -1:
        labelLatencyGoogle.configure(text=f"Latence {HOST2}: {ping_result:9.3f} ms")
    else:
        labelLatencyGoogle.configure(text=f"Latence {HOST2}:   Erreur")
    root.after(1000, getLatencyGoogle)  # Mettre à jour la latence toutes les secondes

def startScan(targets: list[str]) -> dict[str, dict]:
    """Lance un scan réseau et retourne les résultats."""
    try:
        scanner = Scripts.Script_nmap.Scan(targets)
        result: dict[str, dict] = scanner.scan()
        timer = getattr(scanner.scan, 'Debug.Log.Timer', None)

        # Extraire l'adresse IP cible
        target_ip = targets[0] if targets else "N/A"

        # Calculer le nombre réel d'appareils connectés
        connected_devices = len(result['data'][next(iter(result['data']))])  # Nombre d'adresses IP uniques dans les résultats

        # Mesurer la latence pour l'hôte principal
        latency_value = latency.ping()  # Utilisez la classe Latency pour mesurer la latence

        # Enregistrer les résultats dans un fichier JSON
        scanToJson(result, target_ip, connected_devices, latency_value)

        # Envoyer les résultats du scan au serveur Nester
        sendToServer(result, target_ip, connected_devices, latency_value)

        return result, timer
    except Exception as e:
        logger_main.error(f"Erreur lors du scan: {e}")
        return {}, None

def sendToServer(data, target_ip, connected_devices, latency_value):
    """Envoie les données du scan au serveur Nester."""
    # Validation des données
    if not isinstance(data, dict):
        logger_main.error("Les données doivent être un dictionnaire.")
        return

    # Structurer les données pour correspondre au format attendu
    formatted_data = {
        "franchise_id": "franchise_1",  # Doit être une chaîne de caractères
        "ip_address": target_ip,  # Adresse IP scannée
        "connected_devices": connected_devices,  # Nombre réel d'appareils connectés
        "latency": latency_value if latency_value != -1 else 0,  # Latence réelle (ou 0 en cas d'erreur)
        "scan_data": data  # Résultats du scan
    }

    # Envoyer les données au serveur Nester
    try:
        response = requests.post(URL, json=formatted_data)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP non réussis
        logger_main.debug(f"Données envoyées avec succès au serveur Nester: {response.text}")
    except requests.exceptions.RequestException as e:
        logger_main.error(f"Erreur de connexion au serveur Nester: {e}")

def scanToJson(data: dict, target_ip: str, connected_devices: int, latency_value: float):
    """Enregistre les résultats du scan dans un fichier JSON avec une date."""
    if not isinstance(data, dict):
        logger_main.error("Les données doivent être un dictionnaire.")
        return

    # Ajouter un timestamp au fichier JSON
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    scan_filename = f"Scans/scan_{timestamp}.json"

    # Créer le dossier Scans s'il n'existe pas
    if not os.path.exists("Scans"):
        os.makedirs("Scans")

    # Ajouter les champs requis si manquants
    required_fields = ["franchise_id", "ip_address", "connected_devices", "latency", "scan_data"]
    for field in required_fields:
        if field not in data:
            data[field] = "N/A" if field == "ip_address" else 0 if field in ["connected_devices", "latency"] else {}

    # Ajouter l'adresse IP cible, le nombre d'appareils connectés et la latence
    data["ip_address"] = target_ip
    data["connected_devices"] = connected_devices
    data["latency"] = latency_value if latency_value != -1 else 0  # Utiliser 0 si la latence est invalide

    # Enregistrer les résultats dans un fichier JSON
    with open(scan_filename, "w") as f:
        logger_main.debug(f"Copie du résultat en json dans {scan_filename}")
        json.dump(data, f, indent=4)

def listScans():
    """Retourne la liste des fichiers de scans disponibles."""
    if not os.path.exists("Scans"):
        return []

    scans = []
    for filename in os.listdir("Scans"):
        if filename.startswith("scan_") and filename.endswith(".json"):
            scans.append(filename)
    return scans

def openSearchWindow():
    """Ouvre une fenêtre pour rechercher et afficher les scans."""
    search_window = ctk.CTkToplevel(root)
    search_window.title("Rechercher un Scan")
    search_window.geometry("600x400")
    search_window.attributes("-topmost", True)
    search_window.focus_force()

    # Liste des scans disponibles
    scans = listScans()

    # Label et Entry pour la recherche
    ctk.CTkLabel(search_window, text="Rechercher un scan par date (YYYY-MM-DD):").pack(pady=10)
    search_entry = ctk.CTkEntry(search_window)
    search_entry.pack(pady=10)

    # Bouton de recherche
    def performSearch():
        search_date = search_entry.get().strip()
        found_scans = [scan for scan in scans if search_date in scan]

        if found_scans:
            result_textbox.delete("1.0", "end")
            for scan in found_scans:
                result_textbox.insert("end", f"{scan}\n")
        else:
            result_textbox.delete("1.0", "end")
            result_textbox.insert("end", "Aucun scan trouvé pour cette date.")

    search_button = ctk.CTkButton(search_window, text="Rechercher", command=performSearch)
    search_button.pack(pady=10)

    # Zone de texte pour afficher les résultats
    result_textbox = ctk.CTkTextbox(search_window, wrap="none")
    result_textbox.pack(expand=True, fill="both", padx=10, pady=10)

    # Bouton pour ouvrir un scan sélectionné
    def openSelectedScan():
        selected_scan = result_textbox.get("sel.first", "sel.last").strip()
        if selected_scan:
            openScanResults(os.path.join("Scans", selected_scan))

    open_button = ctk.CTkButton(search_window, text="Ouvrir le scan sélectionné", command=openSelectedScan)
    open_button.pack(pady=10)

def openScanResults(scan_file):
    """Ouvre une fenêtre pour afficher les résultats d'un scan spécifique."""
    results_window = ctk.CTkToplevel(root)
    results_window.title("Résultats du Scan")
    results_window.geometry("800x600")
    results_window.attributes("-topmost", True)
    results_window.focus_force()

    # Ajouter un Textbox pour afficher les résultats
    results_textbox = ctk.CTkTextbox(results_window, wrap="none")
    results_textbox.pack(expand=True, fill="both", padx=10, pady=10)

    # Charger les résultats du scan
    if os.path.exists(scan_file):
        with open(scan_file, "r") as f:
            try:
                data = json.load(f)
                results_textbox.insert("1.0", pprint.pformat(data))
            except json.JSONDecodeError as e:
                results_textbox.insert("1.0", f"Erreur de décodage JSON: {e}")
    else:
        results_textbox.insert("1.0", "Fichier de scan introuvable.")

def checkTargetNet(void=None) -> bool:
    """Vérifie si la cible réseau est valide et lance le scan."""
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
        targetNetEntry.configure(state="disabled")
        labelResult.configure(text="Scan en cours ...", bg_color="#fe6807")

        # Lancer le scan réseau dans un thread séparé
        thread = threading.Thread(
            target=lambda: resultQueue.put(startScan([targetNetInput])),
            daemon=True
        )
        thread.start()

        # Vérifier régulièrement si le résultat est prêt
        def check_result():
            try:
                resultat, timer = resultQueue.get_nowait()
                logger_main.debug(f"Résultat du scan : {pprint.pformat(resultat)}")
                labelResult.configure(text=f"Scan terminé", bg_color=color1)
                targetNetBtn.configure(state="normal")
                targetNetEntry.configure(state="normal")
                drawResult(resultat, row)
            except queue.Empty:
                targetNetEntry.after(100, check_result)
            except Exception as e:
                logger_main.error(f"Erreur: {e}")
                labelResult.configure(text="❌ Erreur", bg_color="red")
                targetNetBtn.configure(state="normal")
                targetNetEntry.configure(state="normal")

        check_result()
    else:
        targetNetEntry.configure(border_color="red")
        labelResult.configure(text="❌ Adresse invalide", bg_color="red")

def clearResult() -> None:
    """Efface les résultats précédents du scan."""
    global previousLabel
    for label in previousLabel:
        label.destroy()
    previousLabel.clear()

    # Effacer le contenu de la zone de texte
    if txtBoxResult is not None:
        txtBoxResult.delete("1.0", "end")
        txtBoxResult.destroy()

def drawResult(data: dict, row: int = 0) -> None:
    """Affiche les résultats du scan dans l'interface graphique."""
    logger_main.debug(f"Données reçues : {type(data)} {data}")
    
    clearResult()
    global previousLabel
    previousLabel = []

    # Vérifier que les données sont un dictionnaire
    if not isinstance(data, dict):
        logger_main.error(f"Données invalides : {type(data)}")
        labelResult.configure(text="❌ Données invalides", bg_color="red")
        return

    # Afficher l'adresse IP scannée, le nombre d'appareils connectés et la latence
    if "ip_address" in data:
        ip_label = ctk.CTkLabel(scroll_frame, text=f"IP scannée: {data['ip_address']}", font=("Arial", 12, "bold"))
        ip_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        previousLabel.append(ip_label)
        row += 1

    if "connected_devices" in data:
        devices_label = ctk.CTkLabel(scroll_frame, text=f"Appareils connectés: {data['connected_devices']}", font=("Arial", 12, "bold"))
        devices_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        previousLabel.append(devices_label)
        row += 1

    # Parcourir chaque adresse IP dans les résultats
    for name, detail in data['data'].items():
            hr = ctk.CTkFrame(scroll_frame, width=400, height=2, bg_color=color1, fg_color=color1)
            hr.grid(row=row, columnspan=4, sticky="ew", padx=10, pady=0)
            previousLabel.append(hr)
            row += 1
            label = ctk.CTkLabel(scroll_frame, text=f"Résultat du scan du réseau ou de l'hôte: {name:>15}")
            label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
            previousLabel.append(label)
            row += 1
            for ip, info in detail.items():
                hr = ctk.CTkFrame(scroll_frame, width=400, height=2, bg_color=color3, fg_color=color3)
                hr.grid(row=row, columnspan=4, sticky="ew", padx=10, pady=0)
                previousLabel.append(hr)
                row += 1
                label = ctk.CTkLabel(scroll_frame, text=f"\tIP: {ip}")
                label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=5)
                previousLabel.append(label)
                row += 1
                lat = Scripts.Latency.Latency(ip)
                ping_result = lat.ping()
                logger_main.debug(f"Latence pour {ip}: {lat.ping()}")
                label = ctk.CTkLabel(scroll_frame, text=f"\tLatence: {ip:>15}:{ping_result:9.3f} ms")
                label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=5)
                previousLabel.append(label)
                row += 1
                del lat
                for key, value in info.items():
                    if isinstance(value, dict):
                        label = ctk.CTkLabel(scroll_frame, text=f"\t\t{key}:")
                        label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
                        previousLabel.append(label)
                        row += 1
                        for k, v in value.items():
                            if isinstance(v, dict):
                                label = ctk.CTkLabel(scroll_frame, text=f"\t\t\t{k}:")
                                label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
                                previousLabel.append(label)
                                row += 1
                                for i, j in v.items():
                                    print(f"{name:>15}: {key} -> {k} -> {i} -> {j}")
                                    label = ctk.CTkLabel(scroll_frame, text=f"\t\t\t\t{i}: {j}")
                                    label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
                                    previousLabel.append(label)
                                    row += 1
                            else:
                                print(f"{name:>15}: {key} -> {k} -> {v}")
                                label = ctk.CTkLabel(scroll_frame, text=f"\t\t{key} -> {k} -> {v}")
                                label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
                                previousLabel.append(label)
                                row += 1
                    else:
                        print(f"{name:>15}: {key} -> {value}")
                        label = ctk.CTkLabel(scroll_frame, text=f"\t\t{key}:\t {value}")
                        label.grid(row=row, columnspan=4, sticky="w", padx=10, pady=0)
                        previousLabel.append(label)
                        row += 1

def onHoverIn(btn: ctk.CTkButton) -> None:
    """Change la couleur du bouton lorsque la souris survole."""
    btn.configure(text_color=color2, fg_color=color3)

def onHoverOut(btn: ctk.CTkButton) -> None:
    """Rétablit la couleur du bouton lorsque la souris quitte."""
    btn.configure(text_color=color3, fg_color=color2)

# -------------------- init --------------------

root = ctk.CTk()
screen_width: int = root.winfo_screenwidth()
screen_height: int = root.winfo_screenheight()

color0: str = "white"
color1: str = "#191bdf"  # bleu
color2: str = "#09080d"  # noir
color3: str = "#fe6807"  # orange

root.geometry(f"{screen_width}x{screen_height}")
root.attributes("-fullscreen", True)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("Ressources/Themes/orange.json")

baseFontSize: int = 16

try:
    _monserratBlack: ImageFont.FreeTypeFont = ImageFont.truetype("Ressources/Fonts/Montserrat/static/Montserrat-ExtraBoldItalic.ttf", 2*baseFontSize)
    _loraItalic: ImageFont.FreeTypeFont = ImageFont.truetype("Ressources/Fonts/Lora/static/Lora-Italic.ttf", baseFontSize)
    _hindMadurai: ImageFont.FreeTypeFont = ImageFont.truetype("Ressources/Fonts/Hind_Madurai/HindMadurai-Regular.ttf", baseFontSize)
except IOError as e:
    print(f"Error loading font: {e}")

monserratBlack = ctk.CTkFont(family=_monserratBlack.getname()[0], size=baseFontSize, weight="bold")
loraItalic = ctk.CTkFont(family=_loraItalic.getname()[0], size=baseFontSize, slant="italic")
hindMadurai = ctk.CTkFont(family=_hindMadurai.getname()[0], size=baseFontSize)

root.option_add("*Font", hindMadurai)
root.title("Harvester")

# -------------------- menu --------------------

menuWidth: int = 350
bntY: int = 50

menu = ctk.CTkFrame(root, width=menuWidth, height=30, fg_color=color1, corner_radius=0)
menu.pack(side="left", fill="y")

appName = ctk.CTkLabel(menu, width=menuWidth, height=bntY, text="Harvester", text_color=color0, font=monserratBlack, bg_color=color1)
appName.pack(fill="x")

scanBtn = ctk.CTkButton(menu, width=menuWidth, height=bntY, text="nmap", corner_radius=0)
scanBtn.pack(fill="x")

scanBtn.bind("<Enter>", lambda e: onHoverIn(scanBtn))
scanBtn.bind("<Leave>", lambda e: onHoverOut(scanBtn))

# Ajouter un bouton pour ouvrir la fenêtre de recherche
searchBtn = ctk.CTkButton(menu, width=menuWidth, height=bntY, text="Rechercher un Scan", corner_radius=0, command=openSearchWindow)
searchBtn.pack(fill="x")

searchBtn.bind("<Enter>", lambda e: onHoverIn(searchBtn))
searchBtn.bind("<Leave>", lambda e: onHoverOut(searchBtn))

version = ctk.CTkLabel(menu, width=menuWidth, height=bntY/2, text=getVersion(), text_color=color0, font=loraItalic, bg_color=color1)
version.pack(fill="x", side="bottom")

version = ctk.CTkLabel(menu, width=menuWidth, height=bntY/2, text="Version", text_color=color0, font=monserratBlack, bg_color=color1)
version.pack(fill="x", side="bottom")

quitBtn = ctk.CTkButton(menu, width=menuWidth, height=bntY, text="Quitter", corner_radius=0, command=root.destroy)
quitBtn.pack(fill="x", side="bottom")

quitBtn.bind("<Enter>", lambda e: onHoverIn(quitBtn))
quitBtn.bind("<Leave>", lambda e: onHoverOut(quitBtn))

# -------------------- tab --------------------

txtBoxResult: ctk.CTkTextbox = None

tabScan = ctk.CTkTabview(root)
tabScan.pack(expand=True, fill="both", anchor="w")

tabScan1: ctk.CTkFrame = tabScan.add("Scan")
tabScan1.grid_rowconfigure(0, weight=1)
tabScan1.grid_columnconfigure(0, weight=1)

scroll_frame = ctk.CTkScrollableFrame(tabScan1)
scroll_frame.grid(row=0, column=0, sticky="nsew")

for col in range(4):
    scroll_frame.grid_columnconfigure(col, weight=1, uniform="equal")

row = 0

# Ajouter un champ de saisie pour l'adresse IP ou le réseau
targetNetLabel = ctk.CTkLabel(scroll_frame, text="Réseau à scanner: ")
targetNetLabel.grid(row=row, column=0, pady=10, padx=5, sticky="e")

targetNetEntry = ctk.CTkEntry(scroll_frame, placeholder_text="0.0.0.0/0", placeholder_text_color="gray")
targetNetEntry.grid(row=row, column=1, pady=10, padx=5, sticky="w")

targetNetEntry.bind("<Return>", checkTargetNet)

row += 1

# Ajouter un bouton pour lancer le scan
targetNetBtn = ctk.CTkButton(scroll_frame, text="Lancer le scan NMAP", command=checkTargetNet)
targetNetBtn.grid(row=row, column=0, columnspan=2, pady=10, padx=5)

targetNetBtn.bind("<Enter>", lambda e: onHoverIn(targetNetBtn))
targetNetBtn.bind("<Leave>", lambda e: onHoverOut(targetNetBtn))

row += 1

# Afficher la latence
labelLatency = ctk.CTkLabel(scroll_frame, text=f"Latence vers Datacenter {HOST:>15}: ms")
labelLatency.grid(row=row, columnspan=4, pady=10, padx=5, sticky="w")

row += 1

labelLatencyGoogle = ctk.CTkLabel(scroll_frame, text=f"Latence {HOST2}: ms")
labelLatencyGoogle.grid(row=row, columnspan=4, pady=10, padx=5, sticky="w")

row += 1

# Afficher le résultat du scan
labelResult = ctk.CTkLabel(scroll_frame, text="")
labelResult.grid(row=row, columnspan=4)

row += 1

root.after(1000, getLatency)
root.after(1000, getLatencyGoogle)

# -------------------- loop --------------------

root.mainloop()  # Boucle principale pour maintenir l'interface open