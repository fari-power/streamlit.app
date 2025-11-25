#!/usr/bin/env python3
"""
Création de la carte complète avec tous les points de vente de Casablanca
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import os

def create_complete_map():
    """Crée une carte interactive avec tous les points de vente"""
    
    input_file = "points_vente_casablanca_complet.csv"
    
    if not os.path.exists(input_file):
        print("[ERROR] Fichier de données non trouvé")
        return
    
    print("="*70)
    print("CRÉATION DE LA CARTE COMPLÈTE - CASABLANCA")
    print("="*70)
    
    # Charger les données
    df = pd.read_csv(input_file)
    print(f"[INFO] {len(df)} points de vente charges")
    
    # Nettoyer les coordonnées
    df = df.dropna(subset=['Latitude', 'Longitude'])
    print(f"[INFO] {len(df)} points avec coordonnees valides")
    
    # Centre de Casablanca
    casablanca_center = [33.5731, -7.5898]
    
    # Créer la carte de base
    m = folium.Map(
        location=casablanca_center, 
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Couleurs par statut
    colors = {
        'Formel': 'blue',
        'Informel': 'red'
    }
    
    # Icônes par catégorie
    icons = {
        'Supermarché': 'shopping-cart',
        'Supérette / Mini-market': 'shopping-basket',
        'Épicerie': 'leaf',
        'Café': 'coffee',
        'Restaurant': 'cutlery',
        'Boulangerie': 'grain',
        'Parapharmacie': 'plus-sign',
        'Kiosque': 'home',
        'Boutique de confiserie': 'heart',
        'Magasin bio': 'tree-conifer'
    }
    
    # Créer des clusters par statut
    cluster_formel = MarkerCluster(name=f"Secteur Formel ({len(df[df['Statut']=='Formel'])} points)")
    cluster_informel = MarkerCluster(name=f"Secteur Informel ({len(df[df['Statut']=='Informel'])} points)")
    
    # Ajouter les marqueurs
    for idx, row in df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            
            # Popup avec informations détaillées
            popup_html = f"""
            <div style="width: 250px;">
                <h4>{row['Nom']}</h4>
                <p><b>Catégorie:</b> {row['Catégorie']}</p>
                <p><b>Statut:</b> {row['Statut']}</p>
                <p><b>Zone:</b> {row.get('Zone', 'N/A')}</p>
                <p><b>Adresse:</b> {row.get('Adresse', 'N/A')}</p>
                <p><b>Coordonnées:</b> {row['Latitude']:.4f}, {row['Longitude']:.4f}</p>
            </div>
            """
            
            # Déterminer la couleur et l'icône
            color = colors.get(row['Statut'], 'gray')
            icon_name = icons.get(row['Catégorie'], 'info-sign')
            
            marker = folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['Nom']} ({row['Catégorie']})",
                icon=folium.Icon(
                    color=color, 
                    icon=icon_name,
                    prefix='glyphicon'
                )
            )
            
            # Ajouter au bon cluster
            if row['Statut'] == 'Formel':
                marker.add_to(cluster_formel)
            else:
                marker.add_to(cluster_informel)
    
    # Ajouter les clusters à la carte
    cluster_formel.add_to(m)
    cluster_informel.add_to(m)
    
    # Ajouter une heatmap optionnelle
    heat_data = [[row['Latitude'], row['Longitude']] for idx, row in df.iterrows() 
                 if pd.notna(row['Latitude']) and pd.notna(row['Longitude'])]
    
    heatmap = HeatMap(heat_data, name="Densité des points de vente")
    heatmap.add_to(m)
    
    # Contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Légende détaillée
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px; height: 400px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 15px; overflow-y: auto;">
    
    <h4>Légende - Points de Vente Casablanca</h4>
    
    <p><b>Statuts:</b></p>
    <p><i class="fa fa-circle" style="color:blue"></i> Secteur Formel ({len(df[df['Statut']=='Formel'])} points)</p>
    <p><i class="fa fa-circle" style="color:red"></i> Secteur Informel ({len(df[df['Statut']=='Informel'])} points)</p>
    
    <p><b>Catégories principales:</b></p>
    '''
    
    # Ajouter les statistiques par catégorie
    category_stats = df['Catégorie'].value_counts().head(8)
    for category, count in category_stats.items():
        percentage = count / len(df) * 100
        legend_html += f'<p>• {category}: {count} ({percentage:.1f}%)</p>'
    
    legend_html += f'''
    <p><b>Total:</b> {len(df)} points</p>
    <p><b>Zone:</b> Casablanca et périphérie</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Ajouter des tuiles alternatives
    folium.TileLayer(
        tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
        name='Terrain'
    ).add_to(m)
    folium.TileLayer(
        tiles='CartoDB positron',
        attr='© CartoDB',
        name='CartoDB Light'
    ).add_to(m)
    
    # Sauvegarder
    output_file = "casablanca_points_vente_complet.html"
    m.save(output_file)
    
    print(f"[SUCCESS] Carte complete creee: {output_file}")
    print(f"[INFO] {len(df)} points de vente affiches")
    print(f"[INFO] Secteur Formel: {len(df[df['Statut']=='Formel'])} points")
    print(f"[INFO] Secteur Informel: {len(df[df['Statut']=='Informel'])} points")
    
    return output_file

if __name__ == "__main__":
    map_file = create_complete_map()
    
    # Ouvrir la carte
    if map_file:
        print(f"\n[INFO] Ouverture de la carte...")
        import webbrowser
        try:
            webbrowser.open(map_file)
        except:
            print(f"[INFO] Ouvrez manuellement le fichier: {map_file}")