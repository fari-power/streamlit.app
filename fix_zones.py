#!/usr/bin/env python3
"""
Script pour corriger les zones N/A dans les données
"""

import pandas as pd
import time
from geocode_utils import get_zone

def assign_zones_by_coordinates():
    """Assigne des zones basées sur les coordonnées géographiques"""
    
    # Zones géographiques approximatives de Casablanca basées sur les coordonnées
    zone_mapping = {
        # Centre-ville (autour de la place Mohammed V)
        (33.593, 33.600, -7.630, -7.610): "Centre-Ville",
        
        # Maarif
        (33.575, 33.590, -7.650, -7.630): "Maarif",
        
        # Ain Diab
        (33.570, 33.580, -7.680, -7.650): "Ain Diab",
        
        # Anfa
        (33.590, 33.610, -7.670, -7.640): "Anfa",
        
        # Hay Hassani
        (33.560, 33.580, -7.650, -7.620): "Hay Hassani",
        
        # Sidi Bernoussi
        (33.610, 33.630, -7.550, -7.520): "Sidi Bernoussi",
        
        # Ain Sebaa
        (33.600, 33.620, -7.540, -7.500): "Ain Sebaa",
        
        # Mohammedia (est)
        (33.680, 33.700, -7.390, -7.350): "Mohammedia",
        
        # Bouskoura (sud)
        (33.450, 33.480, -7.650, -7.600): "Bouskoura",
        
        # Nouaceur (sud-ouest)
        (33.360, 33.400, -7.600, -7.550): "Nouaceur",
        
        # Mediouna (sud-est)
        (33.450, 33.480, -7.550, -7.500): "Mediouna",
        
        # Tit Mellil (sud-est)
        (33.540, 33.570, -7.490, -7.460): "Tit Mellil",
        
        # Ain Harrouda (nord-est) 
        (33.630, 33.650, -7.460, -7.430): "Ain Harrouda",
    }
    
    def get_zone_from_coords(lat, lon):
        """Détermine la zone basée sur les coordonnées"""
        if pd.isna(lat) or pd.isna(lon):
            return "Casablanca"
            
        for (lat_min, lat_max, lon_min, lon_max), zone_name in zone_mapping.items():
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return zone_name
        
        # Zones par défaut basées sur la position relative
        if lat > 33.62:
            return "Nord Casablanca"
        elif lat < 33.50:
            return "Sud Casablanca" 
        elif lon < -7.65:
            return "Ouest Casablanca"
        elif lon > -7.45:
            return "Est Casablanca"
        else:
            return "Centre Casablanca"
    
    return get_zone_from_coords

def fix_na_zones():
    """Corrige les valeurs N/A dans la colonne Zone"""
    
    input_file = "points_vente_casablanca_complet.csv"
    
    print("="*70)
    print("CORRECTION DES ZONES N/A")
    print("="*70)
    
    # Charger les données
    df = pd.read_csv(input_file)
    print(f"[INFO] {len(df)} points charges")
    
    # Compter les N/A initiaux
    na_count_initial = df['Zone'].isna().sum() + (df['Zone'] == 'N/A').sum()
    print(f"[INFO] {na_count_initial} zones N/A a corriger")
    
    # Fonction de mapping des zones
    get_zone_func = assign_zones_by_coordinates()
    
    # Corriger les zones N/A
    corrected_count = 0
    
    for idx, row in df.iterrows():
        if pd.isna(row['Zone']) or row['Zone'] == 'N/A':
            # Essayer d'abord le géocodage si possible (avec limite)
            new_zone = None
            
            if corrected_count < 50:  # Limiter les appels à l'API
                try:
                    new_zone = get_zone(row['Latitude'], row['Longitude'])
                    if new_zone and new_zone != 'N/A':
                        df.at[idx, 'Zone'] = new_zone
                        corrected_count += 1
                        time.sleep(0.5)  # Pause pour éviter les timeouts
                        continue
                except:
                    pass
            
            # Utiliser le mapping par coordonnées
            coord_zone = get_zone_func(row['Latitude'], row['Longitude'])
            df.at[idx, 'Zone'] = coord_zone
            corrected_count += 1
    
    # Compter les N/A finaux
    na_count_final = df['Zone'].isna().sum() + (df['Zone'] == 'N/A').sum()
    
    print(f"[INFO] {corrected_count} zones corrigees")
    print(f"[INFO] {na_count_final} zones N/A restantes")
    
    # Statistiques par zone
    print(f"\n[INFO] Repartition par zone:")
    zone_stats = df['Zone'].value_counts().head(15)
    for zone, count in zone_stats.items():
        print(f"   {zone}: {count}")
    
    # Sauvegarder
    output_file = "points_vente_casablanca_zones_corrigees.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n[SUCCESS] Fichier corrige sauvegarde: {output_file}")
    
    return df

def create_map_with_zones():
    """Crée une carte avec les zones corrigées"""
    
    try:
        import folium
        from folium.plugins import MarkerCluster
        
        # Charger les données corrigées
        df = pd.read_csv("points_vente_casablanca_zones_corrigees.csv")
        
        # Nettoyer les coordonnées
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        print(f"[INFO] Creation de la carte avec {len(df)} points")
        
        # Centre de Casablanca
        m = folium.Map(location=[33.5731, -7.5898], zoom_start=11)
        
        # Couleurs par zone (prendre les principales)
        top_zones = df['Zone'].value_counts().head(10).index.tolist()
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
                 'beige', 'darkblue', 'darkgreen']
        
        zone_colors = {zone: colors[i % len(colors)] for i, zone in enumerate(top_zones)}
        
        # Ajouter des marqueurs par zone
        for zone in top_zones:
            zone_df = df[df['Zone'] == zone]
            if len(zone_df) > 0:
                cluster = MarkerCluster(name=f"{zone} ({len(zone_df)} points)")
                
                for idx, row in zone_df.iterrows():
                    popup_html = f"""
                    <b>{row['Nom']}</b><br>
                    Zone: {row['Zone']}<br>
                    Catégorie: {row['Catégorie']}<br>
                    Statut: {row['Statut']}
                    """
                    
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"{row['Nom']} - {row['Zone']}",
                        icon=folium.Icon(
                            color=zone_colors.get(zone, 'gray'),
                            icon='info-sign'
                        )
                    ).add_to(cluster)
                
                cluster.add_to(m)
        
        # Contrôle des couches
        folium.LayerControl().add_to(m)
        
        # Légende
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 300px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; overflow-y: auto;">
        <h4>Zones de Casablanca</h4>
        '''
        
        for zone in top_zones[:8]:
            count = len(df[df['Zone'] == zone])
            color = zone_colors.get(zone, 'gray')
            legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> {zone}: {count}</p>'
        
        legend_html += f'<p><b>Total:</b> {len(df)} points</p></div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Sauvegarder
        map_file = "casablanca_carte_zones_corrigees.html"
        m.save(map_file)
        
        print(f"[SUCCESS] Carte avec zones creee: {map_file}")
        
        return map_file
        
    except ImportError:
        print("[ERROR] Folium non installe")
        return None

if __name__ == "__main__":
    # Corriger les zones
    df_corrected = fix_na_zones()
    
    print("\n" + "="*70)
    print("CRÉATION DE LA CARTE AVEC ZONES CORRIGÉES")
    print("="*70)
    
    # Créer la carte
    map_file = create_map_with_zones()
    
    if map_file:
        print(f"\n[INFO] Carte prete: {map_file}")
        import webbrowser
        try:
            webbrowser.open(map_file)
        except:
            print(f"[INFO] Ouvrez: {map_file}")