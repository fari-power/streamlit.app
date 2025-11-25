#!/usr/bin/env python3
"""
Création d'une carte interactive moderne et belle pour les points de vente de Casablanca
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, FastMarkerCluster, MiniMap
import json
import os

def create_beautiful_interactive_map():
    """Crée une carte interactive moderne avec de belles interactions"""
    
    input_file = "points_vente_casablanca_complet.csv"
    
    if not os.path.exists(input_file):
        print("[ERROR] Fichier de données non trouvé")
        return
    
    print("="*70)
    print("🗺️  CRÉATION D'UNE BELLE CARTE INTERACTIVE - CASABLANCA")
    print("="*70)
    
    # Charger les données
    df = pd.read_csv(input_file)
    print(f"[INFO] {len(df)} points de vente charges")
    
    # Nettoyer les coordonnées
    df = df.dropna(subset=['Latitude', 'Longitude'])
    print(f"[INFO] {len(df)} points avec coordonnees valides")
    
    # Centre de Casablanca
    casablanca_center = [33.5731, -7.5898]
    
    # Créer la carte de base avec un style moderne
    m = folium.Map(
        location=casablanca_center,
        zoom_start=11,
        tiles=None,  # On va ajouter nos propres tuiles
        prefer_canvas=True
    )
    
    # Ajouter différents styles de cartes
    folium.TileLayer(
        'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>',
        name='Style Moderne (Clair)',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>',
        name='Style Moderne (Sombre)',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        name='Style Minimaliste',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        name='Style Classique',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Palette de couleurs moderne
    color_palette = {
        'Supermarché': '#2E8B57',      # Vert forêt
        'Supérette / Mini-market': '#4169E1',  # Bleu royal
        'Épicerie': '#FF6347',         # Tomate
        'Café': '#8B4513',             # Marron selle
        'Restaurant': '#FF4500',       # Orange rouge
        'Boulangerie': '#DAA520',      # Doré
        'Parapharmacie': '#32CD32',    # Vert lime
        'Kiosque': '#9370DB',          # Violet moyen
        'Boutique de confiserie': '#FF69B4',  # Rose vif
        'Magasin bio': '#228B22'       # Vert forêt
    }
    
    # Icônes FontAwesome modernes
    icon_mapping = {
        'Supermarché': 'fa-shopping-cart',
        'Supérette / Mini-market': 'fa-shopping-basket',
        'Épicerie': 'fa-apple-alt',
        'Café': 'fa-coffee',
        'Restaurant': 'fa-utensils',
        'Boulangerie': 'fa-bread-slice',
        'Parapharmacie': 'fa-pills',
        'Kiosque': 'fa-store',
        'Boutique de confiserie': 'fa-candy-cane',
        'Magasin bio': 'fa-leaf'
    }
    
    # Créer des groupes de marqueurs par catégorie avec clustering
    category_groups = {}
    category_stats = df['Catégorie'].value_counts()
    
    for category in category_stats.index:
        category_data = df[df['Catégorie'] == category]
        count = len(category_data)
        
        # Utiliser FastMarkerCluster pour de meilleures performances
        cluster = FastMarkerCluster(
            data=[[row['Latitude'], row['Longitude']] for _, row in category_data.iterrows()],
            name=f"🏪 {category} ({count})",
            callback=(
                "function (row) {"
                f"var icon = L.AwesomeMarkers.icon({{"
                f"icon: '{icon_mapping.get(category, 'fa-store')}',"
                f"markerColor: '{color_palette.get(category, '#666666')}',"
                f"prefix: 'fa'"
                f"}});"
                f"var marker = L.marker(new L.LatLng(row[0], row[1]), {{icon: icon}});"
                f"return marker;"
                "}"
            )
        )
        category_groups[category] = cluster
        cluster.add_to(m)
    
    # Ajouter des marqueurs individuels avec popups riches
    for idx, row in df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            
            # HTML moderne pour le popup
            popup_html = f"""
            <div style="
                width: 320px; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 0;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            ">
                <div style="
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-bottom: 1px solid rgba(255,255,255,0.2);
                ">
                    <h3 style="
                        margin: 0;
                        font-size: 18px;
                        font-weight: 600;
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                    ">
                        <i class="fa {icon_mapping.get(row['Catégorie'], 'fa-store')}" 
                           style="margin-right: 8px; color: #FFD700;"></i>
                        {row['Nom']}
                    </h3>
                </div>
                
                <div style="padding: 15px;">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <i class="fa fa-tag" style="width: 20px; color: #FFD700;"></i>
                        <span style="margin-left: 8px; font-weight: 500;">{row['Catégorie']}</span>
                    </div>
                    
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <i class="fa fa-certificate" style="width: 20px; color: #FFD700;"></i>
                        <span style="margin-left: 8px;">Secteur {row['Statut']}</span>
                    </div>
                    
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <i class="fa fa-map-marker-alt" style="width: 20px; color: #FFD700;"></i>
                        <span style="margin-left: 8px;">{row.get('Zone', 'Casablanca')}</span>
                    </div>
                    
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <i class="fa fa-home" style="width: 20px; color: #FFD700;"></i>
                        <span style="margin-left: 8px; font-size: 12px; opacity: 0.9;">
                            {str(row.get('Adresse', 'N/A'))[:50]}{'...' if len(str(row.get('Adresse', 'N/A'))) > 50 else ''}
                        </span>
                    </div>
                    
                    <div style="
                        background: rgba(255,255,255,0.1);
                        padding: 8px;
                        border-radius: 8px;
                        font-size: 11px;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <i class="fa fa-crosshairs" style="color: #FFD700;"></i>
                        {row['Latitude']:.4f}, {row['Longitude']:.4f}
                    </div>
                </div>
            </div>
            """
            
            # Marqueur avec icône personnalisée
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=340),
                tooltip=folium.Tooltip(
                    f"<b>{row['Nom']}</b><br>{row['Catégorie']}<br>📍 {row.get('Zone', 'Casablanca')}",
                    style="background-color: #2c3e50; color: white; font-family: Arial; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);"
                ),
                icon=folium.Icon(
                    color='darkblue',
                    icon='info-sign',
                    prefix='glyphicon'
                )
            ).add_to(m)
    
    # Ajouter une heatmap avec style moderne
    heat_data = [
        [row['Latitude'], row['Longitude'], 1] 
        for _, row in df.iterrows() 
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude'])
    ]
    
    heatmap = HeatMap(
        heat_data,
        name="🔥 Carte de Densité",
        radius=20,
        blur=15,
        max_zoom=1,
        gradient={
            0.0: '#000080',  # Bleu foncé
            0.2: '#0000FF',  # Bleu
            0.4: '#00FFFF',  # Cyan
            0.6: '#FFFF00',  # Jaune
            0.8: '#FF8000',  # Orange
            1.0: '#FF0000'   # Rouge
        }
    )
    heatmap.add_to(m)
    
    # Ajouter une mini-carte
    minimap = MiniMap(
        tile_layer='CartoDB positron',
        position='bottomright',
        width=150,
        height=100,
        zoom_level_offset=-5
    )
    minimap.add_to(m)
    
    # Contrôle des couches avec style
    layer_control = folium.LayerControl(
        position='topright',
        collapsed=False
    )
    layer_control.add_to(m)
    
    # Ajouter une légende interactive moderne
    legend_html = f'''
    <div id="legend" style="
        position: fixed; 
        top: 10px; 
        left: 10px; 
        width: 350px; 
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border: none;
        border-radius: 15px;
        z-index: 9999; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        overflow: hidden;
        transition: all 0.3s ease;
    ">
        <div style="
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            cursor: pointer;
        " onclick="toggleLegend()">
            <h3 style="
                margin: 0; 
                font-size: 18px; 
                font-weight: 600;
                text-align: center;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            ">
                🗺️ Points de Vente - Casablanca
                <span id="toggleIcon" style="float: right;">▼</span>
            </h3>
        </div>
        
        <div id="legendContent" style="padding: 15px;">
            <div style="margin-bottom: 15px;">
                <h4 style="
                    margin: 0 0 10px 0; 
                    font-size: 14px; 
                    color: #FFD700;
                    border-bottom: 1px solid rgba(255,215,0,0.3);
                    padding-bottom: 5px;
                ">
                    📊 Statistiques Générales
                </h4>
                <p style="margin: 5px 0; font-size: 12px;">
                    📍 <b>Total:</b> {len(df)} points de vente
                </p>
                <p style="margin: 5px 0; font-size: 12px;">
                    🏢 <b>Formel:</b> {len(df[df['Statut']=='Formel'])} ({len(df[df['Statut']=='Formel'])/len(df)*100:.1f}%)
                </p>
                <p style="margin: 5px 0; font-size: 12px;">
                    🏪 <b>Informel:</b> {len(df[df['Statut']=='Informel'])} ({len(df[df['Statut']=='Informel'])/len(df)*100:.1f}%)
                </p>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="
                    margin: 0 0 10px 0; 
                    font-size: 14px; 
                    color: #FFD700;
                    border-bottom: 1px solid rgba(255,215,0,0.3);
                    padding-bottom: 5px;
                ">
                    🏷️ Répartition par Catégorie
                </h4>
    '''
    
    # Ajouter les statistiques par catégorie avec couleurs
    category_stats = df['Catégorie'].value_counts().head(8)
    for category, count in category_stats.items():
        percentage = count / len(df) * 100
        color = color_palette.get(category, '#666666')
        icon = icon_mapping.get(category, 'fa-store')
        legend_html += f'''
        <div style="
            display: flex; 
            align-items: center; 
            margin: 5px 0; 
            padding: 5px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            font-size: 11px;
        ">
            <i class="fa {icon}" style="
                color: {color}; 
                width: 20px; 
                text-align: center;
                margin-right: 8px;
                font-size: 12px;
            "></i>
            <span style="flex: 1;">{category}</span>
            <span style="
                background: {color}; 
                color: white; 
                padding: 2px 6px; 
                border-radius: 10px; 
                font-size: 10px;
                font-weight: bold;
            ">{count}</span>
        </div>
        '''
    
    legend_html += f'''
            </div>
            
            <div style="
                text-align: center; 
                margin-top: 15px; 
                padding-top: 10px; 
                border-top: 1px solid rgba(255,255,255,0.2);
                font-size: 10px;
                opacity: 0.8;
            ">
                💡 Cliquez sur les marqueurs pour plus d'infos<br>
                🎛️ Utilisez les contrôles pour filtrer les données
            </div>
        </div>
    </div>
    
    <script>
        function toggleLegend() {{
            var content = document.getElementById('legendContent');
            var icon = document.getElementById('toggleIcon');
            var legend = document.getElementById('legend');
            
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                icon.innerHTML = '▼';
                legend.style.height = 'auto';
            }} else {{
                content.style.display = 'none';
                icon.innerHTML = '▶';
                legend.style.height = '60px';
            }}
        }}
        
        // Effet de survol sur la légende
        document.getElementById('legend').addEventListener('mouseenter', function() {{
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 15px 40px rgba(0,0,0,0.4)';
        }});
        
        document.getElementById('legend').addEventListener('mouseleave', function() {{
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
        }});
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Ajouter du CSS pour les icônes FontAwesome
    fa_css = '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .leaflet-popup-content {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }
        
        .leaflet-control-layers {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        
        .leaflet-control-zoom {
            border-radius: 10px !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        
        .leaflet-control-zoom a {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 8px !important;
            margin: 2px !important;
        }
    </style>
    '''
    
    m.get_root().html.add_child(folium.Element(fa_css))
    
    # Sauvegarder la carte
    output_file = "casablanca_points_vente_interactive.html"
    m.save(output_file)
    
    print(f"[SUCCESS] 🎉 Belle carte interactive créée: {output_file}")
    print(f"[INFO] ✨ {len(df)} points de vente avec interactions riches")
    print(f"[INFO] 🎨 Design moderne avec animations et couleurs")
    print(f"[INFO] 📱 Interface responsive et intuitive")
    
    return output_file

if __name__ == "__main__":
    map_file = create_beautiful_interactive_map()
    
    # Ouvrir la carte automatiquement
    if map_file:
        print(f"\n[INFO] 🚀 Ouverture de la carte interactive...")
        import subprocess
        try:
            subprocess.run(['start', map_file], shell=True, check=True)
        except:
            print(f"[INFO] 💻 Ouvrez manuellement le fichier: {map_file}")
        
        print(f"\n{'='*70}")
        print("🌟 CARTE INTERACTIVE CRÉÉE AVEC SUCCÈS!")
        print("✨ Fonctionnalités incluses:")
        print("   🎨 Design moderne avec dégradés")
        print("   🖱️  Popups interactifs riches")
        print("   🔥 Carte de densité (heatmap)")
        print("   📊 Légende interactive pliable")
        print("   🗺️  Styles de cartes multiples")
        print("   📱 Interface responsive")
        print("   🎛️  Contrôles de couches avancés")
        print(f"{'='*70}")