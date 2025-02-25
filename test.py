import customtkinter as ctk
import tkinter as tk

def afficher_onglet(onglet, bouton):
    # Masquer tous les onglets
    for widget in right_frame.winfo_children():
        widget.pack_forget()
    
    # Animation de la ligne sous le bouton
    animer_ligne(bouton)
    
    # Afficher l'onglet sélectionné
    onglet.pack(fill="both", expand=True)

def animer_ligne(bouton):
    # Récupérer les coordonnées du bouton pour la ligne
    x1, y1, x2, y2 = bouton.bbox("all")
    ligne.place(x=x1, y=y2 + 5, width=0)  # Initialiser la ligne sous le bouton
    
    # Animation : agrandir progressivement la largeur de la ligne
    for i in range(10, x2 - x1 + 1, 5):
        ligne.place(width=i)  # Agrandir la ligne
        ligne.update()  # Mettre à jour l'affichage
        root.after(20)  # Attendre avant de redimensionner à nouveau

# Fenêtre principale
root = ctk.CTk()
root.geometry("600x400")
root.title("Menu avec animation")

# Création du cadre gauche pour le menu
left_frame = ctk.CTkFrame(root, width=150, height=400, fg_color="lightgray")
left_frame.pack(side="left", fill="y")

# Boutons du menu
menu_button1 = ctk.CTkButton(left_frame, text="Onglet 1", command=lambda: afficher_onglet(onglet1, menu_button1))
menu_button1.pack(pady=10, fill="x")

menu_button2 = ctk.CTkButton(left_frame, text="Onglet 2", command=lambda: afficher_onglet(onglet2, menu_button2))
menu_button2.pack(pady=10, fill="x")

# Dessiner une ligne de séparation (entre menu et onglets)
canvas = tk.Canvas(root, height=2, bg="black", bd=0, highlightthickness=0)
canvas.pack(fill="x")
canvas.create_line(0, 0, 600, 0, fill="black", width=2)

# Création du cadre droit pour les onglets
right_frame = ctk.CTkFrame(root, width=450, height=400)
right_frame.pack(side="right", fill="both", expand=True)

# Onglet 1
onglet1 = ctk.CTkLabel(right_frame, text="Contenu de l'Onglet 1", font=("Arial", 16))
# Onglet 2
onglet2 = ctk.CTkLabel(right_frame, text="Contenu de l'Onglet 2", font=("Arial", 16))

# Création de la ligne animée sous le bouton
ligne = tk.Label(root, bg="blue", height=2)

# Affichage initial de l'onglet 1
afficher_onglet(onglet1, menu_button1)

# Lancer l'application
root.mainloop()
