import customtkinter as ctk
import tkinter as tk
import math

def draw_radial_chart():
    canvas.delete("all")  # Effacer le canvas avant de redessiner
    
    # Définir le centre du graphique
    center_x, center_y = 200, 200
    radius = 100  # Rayon du graphique
    num_axes = 6  # Nombre de dimensions / axes
    
    # Exemple de valeurs entre 0 et 1 (chaque valeur est un pourcentage du rayon)
    values = [0.8, 0.6, 0.9, 0.7, 0.5, 0.8]  # Doit avoir num_axes éléments

    # Dessiner les axes radiaux
    angles = [(2 * math.pi / num_axes) * i for i in range(num_axes)]
    for angle in angles:
        x_end = center_x + radius * math.cos(angle)
        y_end = center_y - radius * math.sin(angle)
        canvas.create_line(center_x, center_y, x_end, y_end, fill="gray", dash=(2, 2))

    # Dessiner les cercles concentriques pour l'échelle
    for i in range(1, 6):  # 5 niveaux
        r = (i / 5) * radius
        canvas.create_oval(center_x - r, center_y - r, center_x + r, center_y + r, outline="lightgray")

    # Convertir les valeurs en coordonnées cartésiennes
    points = []
    for i, value in enumerate(values):
        x = center_x + (value * radius) * math.cos(angles[i])
        y = center_y - (value * radius) * math.sin(angles[i])
        points.append((x, y))
    
    # Dessiner le polygone représentant les valeurs
    canvas.create_polygon(points, fill="#87CEEB", outline="blue", width=2, stipple="gray50")

    # Ajouter des points pour marquer les valeurs
    for x, y in points:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

# Créer la fenêtre principale
root = ctk.CTk()
root.geometry("400x400")

# Ajouter un Canvas pour dessiner le graphique
canvas = ctk.CTkCanvas(root, width=400, height=400)
canvas.pack()

# Ajouter un bouton pour dessiner le graphique
button = ctk.CTkButton(root, text="Dessiner Graphique Radial", command=draw_radial_chart)
button.pack(pady=10)

# Lancer la boucle principale
root.mainloop()
