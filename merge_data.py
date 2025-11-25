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

def merge_all_data():
    """Fusionne toutes les sources de données disponibles"""
    print("[INFO] Demarrage de la fusion des donnees...")
    
    # --- Icônes ---
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
    
    data_frames = []
    
    # Chercher et charger les fichiers OSM
    osm_file = find_latest_file("points_vente_casablanca_osm*.csv")
    if osm_file and osm_file.exists():
        print(f"[INFO] Chargement OSM: {osm_file}")
        df_osm = pd.read_csv(osm_file)
        df_osm['Source'] = 'OSM'
        data_frames.append(df_osm)
        print(f"   [SUCCESS] {len(df_osm)} points OSM charges")
    
    # Chercher et charger les fichiers ATP
    atp_file = find_latest_file("points_vente_casablanca_atp*.csv")
    if atp_file and atp_file.exists():
        print(f"[INFO] Chargement ATP: {atp_file}")
        df_atp = pd.read_csv(atp_file)
        df_atp['Source'] = 'ATP'
        data_frames.append(df_atp)
        print(f"   [SUCCESS] {len(df_atp)} points ATP charges")
    
    # Chercher d'autres fichiers de données
    other_files = [
        "points_vente_casablanca.csv",
        "points_de_vente_casablanca.csv"
    ]
    
    for file_name in other_files:
        if os.path.exists(file_name):
            print(f"[INFO] Chargement fichier supplementaire: {file_name}")
            df_other = pd.read_csv(file_name)
            df_other['Source'] = 'Existant'
            data_frames.append(df_other)
            print(f"   [SUCCESS] {len(df_other)} points charges depuis {file_name}")
    
    if not data_frames:
        print("[ERROR] Aucune donnee trouvee a fusionner")
        return None
    
    # Fusionner tous les DataFrames
    print("[INFO] Fusion des donnees...")
    df_combined = pd.concat(data_frames, ignore_index=True)
    
    # Standardiser les colonnes manquantes
    required_columns = ['Zone', 'Nom', 'Catégorie', 'Statut', 'Adresse', 'Latitude', 'Longitude', 'Image', 'Source']
    for col in required_columns:
        if col not in df_combined.columns:
            if col == 'Image':
                df_combined[col] = df_combined['Catégorie'].map(images).fillna("Aucune image")
            elif col == 'Statut':
                df_combined[col] = 'Formel'
            elif col == 'Zone':
                df_combined[col] = 'Casablanca'
            else:
                df_combined[col] = 'N/A'
    
    # Nettoyer les données
    initial_count = len(df_combined)
    
    # Supprimer les lignes avec des coordonnées invalides
    df_combined = df_combined.dropna(subset=['Latitude', 'Longitude'])
    df_combined = df_combined[(df_combined['Latitude'] != 0) & (df_combined['Longitude'] != 0)]
    
    # Supprimer les doublons
    df_combined = df_combined.drop_duplicates(subset=["Nom", "Latitude", "Longitude"], keep='first')
    
    final_count = len(df_combined)
    removed_count = initial_count - final_count
    
    print(f"[INFO] Nettoyage termine: {removed_count} entrees supprimees ({initial_count} -> {final_count})")
    
    # Sauvegarder le résultat
    output_file = "points_vente_casablanca_merged.csv"
    try:
        df_combined.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] Donnees fusionnees sauvegardees dans {output_file}")
        
        # Créer aussi le fichier avec l'ancien nom pour compatibilité
        df_combined.to_csv("points_vente_casablanca.csv", index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] Copie de compatibilite creee: points_vente_casablanca.csv")
        
        # Afficher les statistiques
        print(f"\n[INFO] === STATISTIQUES FINALES ===")
        print(f"Total points: {len(df_combined)}")
        
        category_stats = df_combined['Catégorie'].value_counts()
        print(f"\nPar categorie:")
        for cat, count in category_stats.items():
            print(f"  {cat}: {count}")
        
        source_stats = df_combined['Source'].value_counts()
        print(f"\nPar source:")
        for source, count in source_stats.items():
            print(f"  {source}: {count}")
        
        return df_combined
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde: {e}")
        return None

if __name__ == "__main__":
    merge_all_data()
