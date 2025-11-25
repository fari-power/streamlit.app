import webbrowser
import os

# Ouvrir la carte principale
map_file = "points_vente_casablanca_map.html"
if os.path.exists(map_file):
    print(f"[INFO] Ouverture de {map_file}...")
    webbrowser.open(f"file://{os.path.abspath(map_file)}")
    print(f"[SUCCESS] Carte ouverte dans le navigateur!")
else:
    print(f"[ERROR] Fichier {map_file} non trouvé")

# Ouvrir aussi la carte simple
simple_map_file = "points_vente_casablanca_simple.html"
if os.path.exists(simple_map_file):
    print(f"[INFO] Carte simple disponible: {simple_map_file}")