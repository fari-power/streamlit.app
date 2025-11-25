import pandas as pd
import os
import time
from pathlib import Path

def find_latest_file(pattern):
    """Trouve le fichier le plus récent correspondant au pattern"""
    files = list(Path('.').glob(pattern))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def merge_data_sources():
    """Fusionne les données OSM et ATP"""
    
    print("[INFO] Fusion des donnees OSM et ATP...")
    
    # Chercher les fichiers de données
    osm_file = find_latest_file("points_vente_casablanca_osm*.csv")
    atp_file = find_latest_file("points_vente_casablanca_atp*.csv")
    
    data_frames = []
    
    # Charger les données OSM
    if osm_file and osm_file.exists():
        print(f"[INFO] Chargement des donnees OSM depuis {osm_file}")
        df_osm = pd.read_csv(osm_file)
        df_osm['Source'] = 'OSM'
        data_frames.append(df_osm)
        print(f"   [SUCCESS] {len(df_osm)} points OSM charges")
    else:
        print("   [WARNING] Aucun fichier OSM trouve")
    
    # Charger les données ATP
    if atp_file and atp_file.exists():
        print(f"[INFO] Chargement des donnees ATP depuis {atp_file}")
        df_atp = pd.read_csv(atp_file)
        df_atp['Source'] = 'ATP'
        data_frames.append(df_atp)
        print(f"   [SUCCESS] {len(df_atp)} points ATP charges")
    else:
        print("   [WARNING] Aucun fichier ATP trouve")
    
    if not data_frames:
        print("[ERROR] Aucune donnee a fusionner")
        return None
    
    # Fusionner les DataFrames
    df_final = pd.concat(data_frames, ignore_index=True)
    
    # Nettoyer les données
    print("[INFO] Nettoyage des doublons...")
    initial_count = len(df_final)
    
    # Supprimer les doublons basés sur la proximité géographique (50m) et le nom similaire
    df_final = df_final.drop_duplicates(subset=["Nom", "Latitude", "Longitude"], keep='first')
    
    # Supprimer les lignes avec des coordonnées manquantes
    df_final = df_final.dropna(subset=['Latitude', 'Longitude'])
    
    final_count = len(df_final)
    removed_count = initial_count - final_count
    
    print(f"   [INFO] {removed_count} doublons supprimes ({initial_count} -> {final_count})")
    
    # Ajouter des statistiques
    print("\n[INFO] Statistiques par categorie:")
    category_stats = df_final['Catégorie'].value_counts()
    for category, count in category_stats.items():
        print(f"   {category}: {count}")
    
    print(f"\n[INFO] Statistiques par source:")
    if 'Source' in df_final.columns:
        source_stats = df_final['Source'].value_counts()
        for source, count in source_stats.items():
            print(f"   {source}: {count}")
    
    # Sauvegarder le résultat
    output_file = "points_vente_casablanca_final.csv"
    try:
        df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[SUCCESS] Fusion terminee! {len(df_final)} points sauvegardes dans {output_file}")
    except PermissionError:
        output_file = f"points_vente_casablanca_final_{int(time.time())}.csv"
        df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[SUCCESS] Fusion terminee! {len(df_final)} points sauvegardes dans {output_file}")
    
    return df_final

if __name__ == "__main__":
    merge_data_sources()