#!/usr/bin/env python3
"""
Script pour analyser et clarifier les sources de données des points de vente
"""

import pandas as pd
import os
from pathlib import Path

def analyze_data_sources():
    """Analyse les différents fichiers de données et leurs sources"""
    
    print("="*70)
    print("ANALYSE DES SOURCES DE DONNEES - POINTS DE VENTE CASABLANCA")
    print("="*70)
    
    files_to_analyze = [
        ("points_vente_casablanca.csv", "Données OSM originales (existantes)"),
        ("points_vente_casablanca_osm.csv", "Données OSM originales (existantes)"),
        ("points_vente_casablanca_osm_new.csv", "Nouvelles données OSM collectées"),
        ("points_vente_casablanca_atp.csv", "Données ATP simulées"),
        ("points_vente_casablanca_final.csv", "Données fusionnées finales")
    ]
    
    for filename, description in files_to_analyze:
        if os.path.exists(filename):
            print(f"\n📁 {filename}")
            print(f"   📝 {description}")
            
            try:
                df = pd.read_csv(filename)
                print(f"   📊 Nombre de points: {len(df)}")
                print(f"   🏷️  Colonnes: {', '.join(df.columns.tolist())}")
                
                # Analyser les catégories
                if 'Catégorie' in df.columns:
                    categories = df['Catégorie'].value_counts()
                    print(f"   🏪 Catégories principales:")
                    for cat, count in categories.head(3).items():
                        print(f"      - {cat}: {count}")
                
                # Analyser les sources si disponible
                if 'Source' in df.columns:
                    sources = df['Source'].value_counts()
                    print(f"   🔍 Sources:")
                    for source, count in sources.items():
                        print(f"      - {source}: {count}")
                
                # Montrer quelques exemples
                print(f"   🎯 Exemples de données:")
                sample_df = df.head(2)
                for idx, row in sample_df.iterrows():
                    name = row.get('Nom', 'N/A')
                    lat = row.get('Latitude', 'N/A')
                    lon = row.get('Longitude', 'N/A')
                    print(f"      - {name} ({lat}, {lon})")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors de la lecture: {e}")
        else:
            print(f"\n❌ {filename} - Fichier non trouvé")
    
    print("\n" + "="*70)
    print("EXPLICATION DES SOURCES")
    print("="*70)
    
    explanations = [
        ("OSM (OpenStreetMap)", "Données RÉELLES collectées depuis la base collaborative OpenStreetMap"),
        ("ATP (AllThePlaces)", "Données SIMULÉES générées pour tests et démonstrations"),
        ("Données originales", "Fichiers pré-existants dans le dossier (origine inconnue)")
    ]
    
    for source, explanation in explanations:
        print(f"\n🏷️  {source}:")
        print(f"   {explanation}")
    
    print(f"\n{'='*70}")
    print("RECOMMANDATIONS")
    print(f"{'='*70}")
    print("✅ Utilisez les données avec Source='OSM' pour des données fiables")
    print("⚠️  Les données ATP sont simulées, à utiliser uniquement pour tests")
    print("❓ Les données sans colonne 'Source' sont d'origine incertaine")

if __name__ == "__main__":
    analyze_data_sources()