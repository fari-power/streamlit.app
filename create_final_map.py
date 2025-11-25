import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import os
from pathlib import Path
import time

def find_latest_file(pattern):
    """Trouve le fichier le plus récent correspondant au pattern"""
    files = list(Path('.').glob(pattern))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def create_color_icons():
    """Crée des icônes colorées pour différentes catégories"""
    color_mapping = {
        "Supermarché": "red",
        "Supérette / Mini-market": "orange", 
        "Épicerie": "green",
        "Café": "brown",
        "Restaurant": "blue",
        "Grossiste / Distributeur régional": "purple",
        "Kiosque": "pink",
        "Boulangerie": "cadetblue",
        "Parapharmacie": "lightgreen",
        "Boutique de confiserie": "lightred",
        "Magasin bio": "darkgreen"
    }
    return color_mapping

def generate_interactive_map():
    """Génère une carte interactive des points de vente"""
    print("[INFO] Generation de la carte interactive...")
    
    # Chercher le fichier de données fusionnées
    data_file = find_latest_file("points_vente_casablanca_final*.csv")
    
    if not data_file or not data_file.exists():
        # Essayer avec d'autres fichiers
        data_file = find_latest_file("points_vente_casablanca_osm*.csv")
        if not data_file or not data_file.exists():
            print("[ERROR] Aucun fichier de donnees trouve")
            return None
    
    print(f"[INFO] Chargement des donnees depuis {data_file}")
    
    try:
        df = pd.read_csv(data_file)
        print(f"[SUCCESS] {len(df)} points charges")
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement: {e}")
        return None
    
    # Nettoyer les données
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]
    
    if len(df) == 0:
        print("[ERROR] Aucune donnee valide trouvee")
        return None
    
    # Créer la carte centrée sur Casablanca
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Ajouter différents types de tuiles
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)
    
    # Créer des groupes de marqueurs par catégorie
    color_mapping = create_color_icons()
    category_groups = {}
    
    for category in df['Catégorie'].unique():
        if pd.notna(category):
            category_groups[category] = folium.FeatureGroup(name=f"{category}")
            m.add_child(category_groups[category])
    
    # Ajouter les marqueurs
    for _, row in df.iterrows():
        category = row['Catégorie']
        color = color_mapping.get(category, 'gray')
        
        # Créer le popup avec les informations
        popup_html = f"""
        <div style="width: 200px;">
            <h4><b>{row['Nom']}</b></h4>
            <p><b>Catégorie:</b> {row['Catégorie']}</p>
            <p><b>Statut:</b> {row.get('Statut', 'N/A')}</p>
            <p><b>Adresse:</b> {row.get('Adresse', 'N/A')}</p>
            <p><b>Zone:</b> {row.get('Zone', 'N/A')}</p>
            {'<p><b>Source:</b> ' + str(row.get('Source', 'N/A')) + '</p>' if 'Source' in row else ''}
            <p><b>Coordonnées:</b> {row['Latitude']:.4f}, {row['Longitude']:.4f}</p>
        </div>
        """
        
        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['Nom']} ({row['Catégorie']})",
            icon=folium.Icon(color=color, icon='info-sign')
        )
        
        if category in category_groups:
            marker.add_to(category_groups[category])
        else:
            marker.add_to(m)
    
    # Ajouter une carte de chaleur si on a assez de points
    if len(df) > 10:
        heat_data = [[row['Latitude'], row['Longitude']] for _, row in df.iterrows()]
        HeatMap(heat_data, name='Carte de chaleur').add_to(m)
    
    # Ajouter le contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Ajouter des statistiques sur la carte
    stats_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px">
    <h4>Statistiques</h4>
    <p><b>Total points:</b> {len(df)}</p>
    """
    
    category_counts = df['Catégorie'].value_counts()
    for category, count in category_counts.head(5).items():
        stats_html += f"<p><b>{category}:</b> {count}</p>"
    
    if 'Source' in df.columns:
        source_counts = df['Source'].value_counts()
        stats_html += "<hr>"
        for source, count in source_counts.items():
            stats_html += f"<p><b>{source}:</b> {count}</p>"
    
    stats_html += "</div>"
    m.get_root().html.add_child(folium.Element(stats_html))
    
    # Sauvegarder la carte
    output_file = "points_vente_casablanca_map.html"
    try:
        m.save(output_file)
        print(f"[SUCCESS] Carte interactive sauvegardee dans {output_file}")
        
        # Créer aussi une version simple
        simple_output = "points_vente_casablanca_simple.html"
        simple_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(simple_map)
        
        for _, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Nom']} - {row['Catégorie']}",
                tooltip=row['Nom']
            ).add_to(marker_cluster)
        
        simple_map.save(simple_output)
        print(f"[SUCCESS] Carte simple sauvegardee dans {simple_output}")
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde: {e}")
        return None

def generate_statistics_report(df):
    """Génère un rapport statistique des données"""
    print(f"\n[INFO] === RAPPORT STATISTIQUE ===")
    print(f"Total des points de vente: {len(df)}")
    
    print(f"\nRepartition par categorie:")
    category_stats = df['Catégorie'].value_counts()
    for category, count in category_stats.items():
        percentage = (count / len(df)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    if 'Source' in df.columns:
        print(f"\nRepartition par source:")
        source_stats = df['Source'].value_counts()
        for source, count in source_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {source}: {count} ({percentage:.1f}%)")
    
    if 'Zone' in df.columns:
        print(f"\nTop 10 des zones:")
        zone_stats = df['Zone'].value_counts().head(10)
        for zone, count in zone_stats.items():
            print(f"  {zone}: {count}")
    
    # Statistiques géographiques
    print(f"\nStatistiques geographiques:")
    print(f"  Latitude min: {df['Latitude'].min():.4f}")
    print(f"  Latitude max: {df['Latitude'].max():.4f}")
    print(f"  Longitude min: {df['Longitude'].min():.4f}")
    print(f"  Longitude max: {df['Longitude'].max():.4f}")

if __name__ == "__main__":
    # Générer la carte
    map_file = generate_interactive_map()
    
    if map_file:
        print(f"\n[SUCCESS] Processus termine avec succes!")
        print(f"Carte disponible: {map_file}")
        
        # Charger les données pour le rapport
        data_file = find_latest_file("points_vente_casablanca_final*.csv")
        if not data_file:
            data_file = find_latest_file("points_vente_casablanca_osm*.csv")
        
        if data_file:
            df = pd.read_csv(data_file)
            generate_statistics_report(df)
    else:
        print("[ERROR] Echec de la generation de la carte")