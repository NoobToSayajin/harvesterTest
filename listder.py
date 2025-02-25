import customtkinter as ctk

def on_select(event):
    """Mettre à jour le texte en fonction de l'élément sélectionné."""
    selected_value = combo.get()
    if selected_value == "Fruits - Pomme":
        text_label.config(text="Vous avez choisi une Pomme !")
    elif selected_value == "Fruits - Banane":
        text_label.config(text="Vous avez choisi une Banane !")
    elif selected_value == "Fruits - Orange":
        text_label.config(text="Vous avez choisi une Orange !")
    elif selected_value == "Légumes - Carotte":
        text_label.config(text="Vous avez choisi une Carotte !")
    elif selected_value == "Légumes - Brocoli":
        text_label.config(text="Vous avez choisi du Brocoli !")
    elif selected_value == "Légumes - Épinards":
        text_label.config(text="Vous avez choisi des Épinards !")

# Création de la fenêtre
root = ctk.CTk()
root.geometry("400x300")

# Création de la liste déroulante avec des éléments
options = [
    "Fruits - Pomme",
    "Fruits - Banane",
    "Fruits - Orange",
    "Légumes - Carotte",
    "Légumes - Brocoli",
    "Légumes - Épinards"
]

combo = ctk.CTkComboBox(root, values=options, width=300)
combo.pack(pady=20)

# Création du label pour afficher le texte en fonction du choix
text_label = ctk.CTkLabel(root, text="Choisissez un fruit ou un légume", width=300)
text_label.pack(pady=20)

# Lier la sélection dans la combobox à la fonction on_select
combo.bind("<<ComboboxSelected>>", on_select)

root.mainloop()
