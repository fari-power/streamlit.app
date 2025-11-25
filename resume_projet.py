#!/usr/bin/env python3
"""
Script de résumé du projet de points de vente à Casablanca
"""
import pandas as pd
import os
from pathlib import Path

def afficher_resume_projet():
    """Affiche un résumé complet du projet"""
    print("=" * 80)
    print("                    PROJET POINTS DE VENTE CASABLANCA                    ")
    print("=" * 80)
    print()
    
    # Vérifier les fichiers générés
    fichiers_generes = [
        ("points_vente_casablanca_atp*.csv", "Donnees ATP simulees"),
        ("points_vente_casablanca_osm*.csv", "Donnees OpenStreetMap"),
        ("points_vente_casablanca_final.csv", "Fusion OSM + ATP"), 
        ("points_vente_casablanca_merged.csv", "Fusion complete"),
        ("points_vente_casablanca_map.html", "Carte interactive principale"),
        ("points_vente_casablanca_simple.html", "Carte simple"),
        ("points_vente_casablanca.html", "Carte existante")
    ]
    
    print("1. FICHIERS GENERES:")
    print("-" * 40)
    
    for pattern, description in fichiers_generes:
        files = list(Path('.').glob(pattern))
        if files:
            latest_file = max(files, key=os.path.getctime)
            size = os.path.getsize(latest_file)
            print(f"   ✓ {latest_file} ({size:,} bytes)")
            print(f"     -> {description}")
        else:
            print(f"   ✗ {pattern} (non trouve)")
    
    print()
    
    # Analyser les données finales
    try:
        df_final = pd.read_csv("points_vente_casablanca_final.csv")
        print("2. STATISTIQUES DES DONNEES FINALES:")
        print("-" * 40)
        print(f"   Total points de vente: {len(df_final):,}")
        print()
        
        print("   Par categorie:")
        for cat, count in df_final['Catégorie'].value_counts().items():
            pct = (count / len(df_final)) * 100
            print(f"     • {cat}: {count} ({pct:.1f}%)")
        
        print()
        print("   Par source de donnees:")
        if 'Source' in df_final.columns:
            for source, count in df_final['Source'].value_counts().items():
                pct = (count / len(df_final)) * 100
                print(f"     • {source}: {count} ({pct:.1f}%)")
        
        print()
        print("   Zones les plus representees:")
        top_zones = df_final['Zone'].value_counts().head(5)
        for zone, count in top_zones.items():
            print(f"     • {zone}: {count} etablissements")
            
    except Exception as e:
        print(f"   Erreur lors de l'analyse: {e}")
    
    print()
    print("3. OUTILS ET SCRIPTS DISPONIBLES:")
    print("-" * 40)
    
    scripts = {
        "execute_all.py": "Lance tout le processus complet",
        "atp_scraper.py": "Genere des donnees AllThePlaces simulees", 
        "osm_scraper.py": "Collecte depuis OpenStreetMap",
        "fusion_data.py": "Fusionne OSM et ATP",
        "merge_data.py": "Fusion complete de toutes sources",
        "create_final_map.py": "Genere la carte interactive",
        "open_map.py": "Ouvre la carte dans le navigateur",
        "geocode_utils.py": "Utilitaires de geocodage"
    }
    
    for script, desc in scripts.items():
        if os.path.exists(script):
            print(f"   ✓ {script} - {desc}")
        else:
            print(f"   ✗ {script} - {desc} (manquant)")
    
    print()
    print("4. UTILISATION:")
    print("-" * 40)
    print("   Pour executer tout le processus:")
    print("     python execute_all.py")
    print()
    print("   Pour generer seulement la carte:")
    print("     python create_final_map.py")
    print()
    print("   Pour ouvrir la carte:")
    print("     python open_map.py")
    
    print()
    print("5. FICHIERS DE SORTIE PRINCIPAUX:")
    print("-" * 40)
    print("   • points_vente_casablanca_final.csv  -> Donnees fusionnees")
    print("   • points_vente_casablanca_map.html   -> Carte interactive")
    print("   • points_vente_casablanca_simple.html -> Carte simple")
    
    print()
    print("=" * 80)
    print("                              PROJET TERMINE !                              ")
    print("=" * 80)

if __name__ == "__main__":
    afficher_resume_projet()