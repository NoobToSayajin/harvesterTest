import customtkinter as ctk
import tkinter as tk
import random

# Liste initiale de points
points = [(50, 200), (100, 150), (150, 100), (200, 50), (250, 75), (300, 125)]

def draw_graph():
    """Dessine le graphique à partir des points actuels."""
    canvas.delete("all")
    
    # Ajouter les labels pour les axes
    canvas.create_text(355, 250, text="Temps (s)", anchor="w")
    canvas.create_text(50, 45, text="Latences (ms)", anchor="s")
    
    # Dessiner la ligne du graphique
    for i in range(1, len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
    
    # Remplir la zone sous la courbe
    polygon_points = [(50, 250)] + points + [(300, 250)]
    canvas.create_polygon(polygon_points, fill="#87CEEB", outline="blue", stipple="gray50")
    
    # Dessiner les axes
    canvas.create_line(50, 250, 350, 250, arrow=tk.LAST, width=2)  # Axe X
    canvas.create_line(50, 250, 50, 50, arrow=tk.LAST, width=2)    # Axe Y

def update_graph():
    """Met à jour les valeurs et redessine le graphique."""
    global points
    
    # Déplacer tous les points vers la gauche et ajouter un nouveau point à droite
    points = [(x + 50, max(50, min(250, y + random.randint(-20, 20)))) for x, y in points[1:]]  # Décale vers la gauche
    new_x = points[-1][0] + 50
    new_y = random.randint(50, 250)  # Un nouveau point avec une latence aléatoire
    points.append((new_x, new_y))  # Ajouter le nouveau point à droite
    
    draw_graph()
    
    # Planifier la prochaine mise à jour dans 1 seconde
    root.after(1000, update_graph)

# Créer la fenêtre principale
root = ctk.CTk()

# Ajouter un Canvas pour dessiner le graphique
canvas = ctk.CTkCanvas(root, width=400, height=300)
canvas.pack()

# Ajouter un bouton pour actualiser le graphique
button = ctk.CTkButton(root, text="Forcer Mise à Jour", command=update_graph)
button.pack(pady=10)

# Lancer l'affichage initial et démarrer la mise à jour automatique
draw_graph()
root.after(1000, update_graph)

# Lancer la boucle principale
root.mainloop()
