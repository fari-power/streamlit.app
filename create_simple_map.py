#!/usr/bin/env python3
"""
Création d'une carte simple et élégante pour Casablanca
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import os

def create_simple_elegant_map():
    """Crée une carte simple et élégante"""
    
    input_file = "points_vente_casablanca_complet.csv"
    
    if not os.path.exists(input_file):
        print("[ERROR] Fichier de données non trouvé")
        return
    
    print("🗺️  CRÉATION D'UNE CARTE SIMPLE ET ÉLÉGANTE")
    print("=" * 50)
    
    # Charger les données
    df = pd.read_csv(input_file)
    print(f"📊 {len(df)} points de vente chargés")
    
    # Nettoyer les coordonnées
    df = df.dropna(subset=['Latitude', 'Longitude'])
    print(f"✅ {len(df)} points avec coordonnées valides")
    
    # Centre de Casablanca
    casablanca_center = [33.5731, -7.5898]
    
    # Créer la carte de base - simple et propre
    m = folium.Map(
        location=casablanca_center,
        zoom_start=11,
        tiles='CartoDB positron',  # Style épuré
        prefer_canvas=True
    )
    
    # Couleurs simples et agréables
    colors = {
        'Parapharmacie': '#2ECC71',      # Vert
        'Café': '#8B4513',               # Marron
        'Restaurant': '#E74C3C',         # Rouge
        'Supermarché': '#3498DB',        # Bleu
        'Supérette / Mini-market': '#9B59B6',  # Violet
        'Boulangerie': '#F39C12',        # Orange
        'Épicerie': '#E67E22',           # Orange foncé
        'Kiosque': '#34495E',            # Gris foncé
        'Boutique de confiserie': '#E91E63',  # Rose
        'Magasin bio': '#27AE60'         # Vert foncé
    }
    
    # Ajouter les marqueurs par catégorie
    category_stats = df['Catégorie'].value_counts()
    
    for category in category_stats.index[:8]:  # Top 8 catégories
        if category in colors:
            category_data = df[df['Catégorie'] == category]
            
            # Cluster pour cette catégorie
            cluster = MarkerCluster(
                name=f"{category} ({len(category_data)})",
                options={'disableClusteringAtZoom': 15}
            )
            
            for _, row in category_data.iterrows():
                # Popup simple mais informatif
                popup_html = f"""
                <div style="width: 250px; font-family: Arial, sans-serif;">
                    <h4 style="margin: 0 0 10px 0; color: {colors[category]}; 
                               border-bottom: 2px solid {colors[category]}; 
                               padding-bottom: 5px;">
                        {row['Nom']}
                    </h4>
                    <p style="margin: 5px 0;"><strong>Type:</strong> {category}</p>
                    <p style="margin: 5px 0;"><strong>Statut:</strong> 
                       <span style="background: {'#27AE60' if row['Statut'] == 'Formel' else '#E74C3C'}; 
                                    color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">
                           {row['Statut']}
                       </span>
                    </p>
                    <p style="margin: 5px 0;"><strong>Zone:</strong> {row.get('Zone', 'Casablanca')}</p>
                    <p style="margin: 5px 0; color: #666; font-size: 12px;">
                        📍 {row['Latitude']:.4f}, {row['Longitude']:.4f}
                    </p>
                </div>
                """
                
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{row['Nom']} - {category}",
                    icon=folium.Icon(
                        color='white',
                        icon_color=colors[category],
                        icon='info-sign',
                        prefix='glyphicon'
                    )
                ).add_to(cluster)
            
            cluster.add_to(m)
    
    # Heatmap simple
    heat_data = [
        [row['Latitude'], row['Longitude']] 
        for _, row in df.iterrows()
    ]
    
    heatmap = HeatMap(
        heat_data,
        name="Densité",
        radius=15,
        blur=10,
        min_opacity=0.2
    )
    heatmap.add_to(m)
    
    # Contrôle des couches
    folium.LayerControl(position='topright').add_to(m)
    
    # Légende simple et propre
    total_points = len(df)
    formel_count = len(df[df['Statut'] == 'Formel'])
    informel_count = len(df[df['Statut'] == 'Informel'])
    
    legend_html = f'''
    <div style="
        position: fixed;
        top: 10px;
        left: 10px;
        width: 280px;
        background: white;
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 9999;
    ">
        <h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">
            📍 Points de Vente - Casablanca
        </h3>
        
        <div style="margin-bottom: 15px; text-align: center;">
            <div style="display: inline-block; margin: 0 10px;">
                <div style="font-size: 24px; font-weight: bold; color: #3498DB;">{total_points}</div>
                <div style="font-size: 12px; color: #666;">Total</div>
            </div>
            <div style="display: inline-block; margin: 0 10px;">
                <div style="font-size: 18px; font-weight: bold; color: #27AE60;">{formel_count}</div>
                <div style="font-size: 12px; color: #666;">Formel</div>
            </div>
            <div style="display: inline-block; margin: 0 10px;">
                <div style="font-size: 18px; font-weight: bold; color: #E74C3C;">{informel_count}</div>
                <div style="font-size: 12px; color: #666;">Informel</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">Principales catégories:</h4>
    '''
    
    # Top 5 catégories
    for category, count in category_stats.head(5).items():
        if category in colors:
            percentage = count / total_points * 100
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="
                    width: 12px; 
                    height: 12px; 
                    background: {colors[category]}; 
                    border-radius: 50%; 
                    margin-right: 8px;
                "></div>
                <span style="flex: 1; font-size: 14px;">{category}</span>
                <span style="font-size: 12px; color: #666; font-weight: bold;">
                    {count} ({percentage:.1f}%)
                </span>
            </div>
            '''
    
    legend_html += '''
        </div>
        
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; 
                    text-align: center; font-size: 11px; color: #999;">
            💡 Cliquez sur les marqueurs pour plus d'infos
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # CSS simple pour améliorer l'apparence
    css_style = '''
    <style>
        .leaflet-popup-content-wrapper {
            border-radius: 8px;
        }
        
        .leaflet-tooltip {
            background: #2c3e50;
            border: none;
            border-radius: 4px;
            color: white;
            font-weight: 500;
        }
        
        .leaflet-control-layers {
            border-radius: 8px;
            border: 2px solid #ddd;
        }
    </style>
    '''
    
    m.get_root().html.add_child(folium.Element(css_style))
    
    # Sauvegarder
    output_file = "casablanca_simple_elegant.html"
    m.save(output_file)
    
    print(f"✅ Carte créée: {output_file}")
    print(f"📊 {len(category_stats)} catégories affichées")
    print(f"🎨 Style simple et propre")
    
    return output_file

if __name__ == "__main__":
    map_file = create_simple_elegant_map()
    
    if map_file:
        print(f"\n🌟 Ouverture de la carte...")
        import subprocess
        try:
            subprocess.run(['start', map_file], shell=True, check=True)
        except:
            print(f"💻 Ouvrez manuellement: {map_file}")
        
        print(f"\n{'='*50}")
        print("🎉 CARTE SIMPLE ET ÉLÉGANTE CRÉÉE!")
        print("✨ Caractéristiques:")
        print("   🎨 Design épuré et moderne")
        print("   📊 Légende claire et informative")
        print("   🖱️ Navigation intuitive")
        print("   📍 Popups bien structurés")
        print("   🔍 Clustering intelligent")
        print(f"{'='*50}")