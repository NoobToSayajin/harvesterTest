import customtkinter as ctk
import tkinter as tk

def draw_graph():
    # Effacer le canvas avant de redessiner
    canvas.delete("all")
    
    # Ajouter les labels pour les axes
    canvas.create_text(355, 250, text="Temps (s)", anchor="w")
    canvas.create_text(50, 45, text="Latences (ms)", anchor="s")
    
    # Coordonnées pour la courbe
    points = [(50, 200), (100, 150), (150, 100), (200, 50), (250, 75), (300, 125)]
    
    # Dessiner la ligne du graphique
    for i in range(1, len(points)):
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
    
    # Remplir la zone sous la courbe avec une couleur transparente (RGBA)
    polygon_points = [(50, 250)] + points + [(300, 250)]  # Ajouter la base du graphique
    canvas.create_polygon(polygon_points, fill="#87CEEB", outline="blue", stipple="gray50")
    
    # Dessiner les axes des abscisses et ordonnées
    canvas.create_line(50, 250, 350, 250, arrow=tk.LAST, width=2)  # Axe X
    canvas.create_line(50, 250, 50, 50, arrow=tk.LAST, width=2)    # Axe Y

# Créer la fenêtre principale
root = ctk.CTk()

# Ajouter un Canvas pour dessiner le graphique
canvas = ctk.CTkCanvas(root, width=400, height=300)
canvas.pack()

# Ajouter un bouton pour dessiner le graphique
button = ctk.CTkButton(root, text="Dessiner Graphique", command=draw_graph)
button.pack(pady=10)

# Lancer la boucle principale
root.mainloop()
