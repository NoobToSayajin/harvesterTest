import customtkinter as ctk

# Création de la fenêtre principale
root = ctk.CTk()
root.geometry("500x300")
root.title("Formulaire avancé")

# Configuration des colonnes pour un bon redimensionnement
root.grid_columnconfigure(1, weight=1)  # La colonne 1 (inputs) s'étire

# Labels & Inputs
ctk.CTkLabel(root, text="Nom :").grid(row=0, column=0, padx=10, pady=5, sticky="e")
nom_entry = ctk.CTkEntry(root)
nom_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

ctk.CTkLabel(root, text="Email :").grid(row=1, column=0, padx=10, pady=5, sticky="e")
email_entry = ctk.CTkEntry(root)
email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

ctk.CTkLabel(root, text="Mot de passe :").grid(row=2, column=0, padx=10, pady=5, sticky="e")
password_entry = ctk.CTkEntry(root, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# Case à cocher
remember_me = ctk.CTkCheckBox(root, text="Se souvenir de moi")
remember_me.grid(row=3, column=1, pady=10, sticky="w")

# Bouton de validation (centré et large)
submit_button = ctk.CTkButton(root, text="Envoyer")
submit_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

root.mainloop()
