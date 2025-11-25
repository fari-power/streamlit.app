import pandas as pd
import time
import os
from geocode_utils import get_zone

# --- Icônes ---
os.makedirs("icons", exist_ok=True)
images = {
    "Supermarché": "icons/supermarket.png",
    "Supérette / Mini-market": "icons/convenience.png",
    "Épicerie": "icons/greengrocer.png",
    "Café": "icons/cafe.png",
    "Restaurant": "icons/restaurant.png",
    "Grossiste / Distributeur régional": "icons/wholesale.png",
    "Kiosque": "icons/kiosk.png",
    "Boulangerie": "icons/bakery.png",
    "Parapharmacie": "icons/pharmacy.png",
    "Boutique de confiserie": "icons/confectionery.png",
    "Magasin bio": "icons/organic.png",
}

# --- Catégories par enseigne ---
categories = {
    "Carrefour": ("Supermarché", "Formel"),
    "Marjane": ("Supermarché", "Formel"),
    "BIM": ("Supérette / Mini-market", "Formel"),
    "Acima": ("Supérette / Mini-market", "Formel"),
    "LabelVie": ("Supermarché", "Formel"),
    "Paul": ("Boulangerie", "Formel"),
    "McDonald's": ("Restaurant", "Formel"),
    "KFC": ("Restaurant", "Formel"),
    "Brioche Dorée": ("Boulangerie", "Formel"),
    "Domino's Pizza": ("Restaurant", "Formel"),
    "Starbucks": ("Café", "Formel"),
    "Subway": ("Restaurant", "Formel"),
    "Pizza Hut": ("Restaurant", "Formel"),
    "Amoud": ("Magasin bio", "Formel"),
    "La Vie Claire": ("Magasin bio", "Formel"),
    "Auchan": ("Supermarché", "Formel")
}

data_atp = []

# Liste des enseignes alimentaires ATP disponibles au Maroc avec coordonnées simulées


print("[INFO] Generation des donnees ATP simulees...")

for brand, locations in enseignes_data.items():
    cat, statut = categories.get(brand, ("Supermarché", "Formel"))
    image = images.get(cat, "Aucune image")
    
    for i, (lat, lon, quartier) in enumerate(locations):
        zone = get_zone(lat, lon)
        data_atp.append({
            "Zone": zone,
            "Nom": f"{brand} {quartier}",
            "Catégorie": cat,
            "Statut": statut,
            "Adresse": f"Avenue {quartier}, Casablanca",
            "Latitude": lat,
            "Longitude": lon,
            "Image": image
        })
        time.sleep(0.5)  # Petit délai pour le géocodage

# Ajout d'autres enseignes avec données simulées
autres_enseignes = ["Paul", "Brioche Dorée", "Domino's Pizza", "Starbucks", "Subway", "Pizza Hut"]
for i, brand in enumerate(autres_enseignes):
    cat, statut = categories.get(brand, ("Restaurant", "Formel"))
    image = images.get(cat, "Aucune image")
    
    # Coordonnées simulées autour de Casablanca
    lat = 33.5731 + (i * 0.01) - 0.02
    lon = -7.5898 + (i * 0.008) - 0.02
    zone = get_zone(lat, lon)
    
    data_atp.append({
        "Zone": zone,
        "Nom": f"{brand} Casablanca Centre",
        "Catégorie": cat,
        "Statut": statut,
        "Adresse": f"Centre Commercial, Casablanca",
        "Latitude": lat,
        "Longitude": lon,
        "Image": image
    })

df_atp = pd.DataFrame(data_atp)

# Gestion des erreurs de permission pour l'écriture du fichier
output_file = "points_vente_casablanca_atp.csv"
try:
    df_atp.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] ATP : {len(df_atp)} points generes dans {output_file}")
except PermissionError:
    output_file = f"points_vente_casablanca_atp_{int(time.time())}.csv"
    df_atp.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] ATP : {len(df_atp)} points generes dans {output_file}")
