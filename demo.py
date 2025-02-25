import customtkinter as ctk
import tkinter.font as tkFont
from PIL import ImageFont

root = ctk.CTk()
root.geometry("800x600")

baseFontSize: int = 16

_monserratBlack: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Montserrat\\static\\Montserrat-Black.ttf", baseFontSize)
_loraItalic: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Lora\\static\\Lora-Italic.ttf", baseFontSize)
_hindMadurai: ImageFont.FreeTypeFont  = ImageFont.truetype("Ressources\\Fonts\\Hind_Madurai\\HindMadurai-Regular.ttf", baseFontSize)

monserratBlack = tkFont.Font(family=_monserratBlack.getname()[0], size=baseFontSize)
loraItalic = tkFont.Font(family=_loraItalic.getname()[0], size=baseFontSize)
hindMadurai = tkFont.Font(family=_hindMadurai.getname()[0], size=baseFontSize)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root.option_add("*Font", hindMadurai)
root.title("Harvester")

# label
label = ctk.CTkLabel(root, text="label text")
label.pack(pady=10)

# input
entry = ctk.CTkEntry(root, placeholder_text="entry mescouilles", placeholder_text_color="red", text_color="white")
entry.pack(pady=10)

# Fonction pour bouton
def afficher_nom():
    nom: str = entry.get()
    label.configure(text=f"Bonjour, {nom}!")

btn = ctk.CTkButton(root, text="valider", command=afficher_nom)
btn.pack(pady=10)

# Création des onglets
tabview = ctk.CTkTabview(root)
tabview.pack(expand=True, fill="both", padx=10, pady=10)

# Ajout des onglets
tab1: ctk.CTkFrame = tabview.add("Accueil")
tab2: ctk.CTkFrame = tabview.add("Paramètres")

# Contenu des onglets
label1 = ctk.CTkLabel(tab1, text="Bienvenue sur l'onglet Accueil", font=("Arial", 14))
label1.pack(pady=20)

label2 = ctk.CTkLabel(tab2, text="Réglages disponibles ici", font=("Arial", 14))
label2.pack(pady=20)

root.mainloop()