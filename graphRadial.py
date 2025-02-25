import customtkinter as ctk
import tkinter as tk
import math

class RadialGraph:
    def __init__(self, canvas):
        self.canvas = canvas
        self.center_x, self.center_y = 150, 150  # Centre du cercle
        self.radius_outer = 100
        self.radius_inner = 80  # Épaisseur des segments
        self.segments = [
            (0, 90, "red"),
            (90, 180, "blue"),
            (180, 270, "green"),
            (270, 360, "orange")
        ]
        self.current_segment = 0  # Indice du segment en cours
        self.current_angle = 0  # Angle animé en cours

    def draw_segment(self):
        """Anime un segment du graphique radial."""
        if self.current_segment >= len(self.segments):
            return  # Animation terminée
        
        start, end, color = self.segments[self.current_segment]

        if self.current_angle < end:
            self.current_angle += 2  # Incrémentation progressive
            self.canvas.delete("all")  # Effacer le canvas

            # Redessiner tous les segments déjà complétés
            for i in range(self.current_segment):
                s, e, c = self.segments[i]
                self.draw_arc(s, e, c)

            # Dessiner le segment actuel en cours d'animation
            self.draw_arc(start, self.current_angle, color)

            # Reprogrammer la prochaine image
            self.canvas.after(10, self.draw_segment)
        else:
            self.current_segment += 1  # Passer au segment suivant
            self.current_angle = start  # Réinitialiser pour le prochain segment
            self.canvas.after(500, self.draw_segment)  # Pause avant le segment suivant

    def draw_arc(self, start, end, color):
        """Dessine un segment avec des extrémités carrées."""
        start_rad = math.radians(start)
        end_rad = math.radians(end)

        x1_out, y1_out = self.center_x + self.radius_outer * math.cos(start_rad), self.center_y - self.radius_outer * math.sin(start_rad)
        x2_out, y2_out = self.center_x + self.radius_outer * math.cos(end_rad), self.center_y - self.radius_outer * math.sin(end_rad)

        x1_in, y1_in = self.center_x + self.radius_inner * math.cos(start_rad), self.center_y - self.radius_inner * math.sin(start_rad)
        x2_in, y2_in = self.center_x + self.radius_inner * math.cos(end_rad), self.center_y - self.radius_inner * math.sin(end_rad)

        # Dessiner l'arc principal
        self.canvas.create_arc(50, 50, 250, 250, start=start, extent=end - start, outline=color, width=20, style=tk.ARC)

        # Ajouter des extrémités carrées avec des lignes
        self.canvas.create_line(x1_out, y1_out, x1_in, y1_in, fill=color, width=20)
        self.canvas.create_line(x2_out, y2_out, x2_in, y2_in, fill=color, width=20)

        # Cercle intérieur (effet de jauge)
        self.canvas.create_oval(100, 100, 200, 200, fill="white", outline="")

# Interface principale
root = ctk.CTk()
canvas = ctk.CTkCanvas(root, width=300, height=300)
canvas.pack()

graph = RadialGraph(canvas)

button = ctk.CTkButton(root, text="Démarrer Animation", command=graph.draw_segment)
button.pack(pady=10)

root.mainloop()
