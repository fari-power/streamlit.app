import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

df = pd.read_csv("points_vente_casablanca.csv")

# --- Icons ---
icons = {
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

mapa = folium.Map(location=[33.5731, -7.5898], zoom_start=12)
marker_cluster = MarkerCluster().add_to(mapa)

for _, row in df.iterrows():
    icon_path = icons.get(row["Catégorie"])
    if icon_path and os.path.exists(icon_path):
        icon = folium.CustomIcon(icon_path, icon_size=(30,30))
    else:
        icon = folium.Icon(color="blue", icon="info-sign")
    
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"<b>{row['Nom']}</b><br>{row['Catégorie']} - {row['Statut']}<br>{row['Adresse']}",
        icon=icon
    ).add_to(marker_cluster)

mapa.save("points_vente_casablanca.html")
print("✅ Carte interactive enregistrée")
