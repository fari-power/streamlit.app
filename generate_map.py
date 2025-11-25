import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

df = pd.read_csv("points_de_vente_casablanca.csv")
mapa = folium.Map(location=[33.5731, -7.5898], zoom_start=12)
marker_cluster = MarkerCluster().add_to(mapa)

for _, row in df.iterrows():
    if row["Image"] != "Aucune image" and os.path.exists(row["Image"]):
        icon = folium.CustomIcon(row["Image"], icon_size=(30, 30))
    else:
        icon = folium.Icon(color="blue", icon="info-sign")

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"<b>{row['Nom']}</b><br>{row['Catégorie']} - {row['Statut']}<br>{row['Adresse']}<br>Zone: {row['Zone']}",
        icon=icon
    ).add_to(marker_cluster)

mapa.save("points_casablanca.html")
print("✅ Carte interactive enregistrée")
