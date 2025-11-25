#!/usr/bin/env python3
"""
Résumé final du projet de collecte des points de vente à Casablanca
"""

import pandas as pd
import os

def generate_final_summary():
    """Génère un résumé complet du projet"""
    
    print("="*80)
    print("RÉSUMÉ FINAL - PROJET POINTS DE VENTE CASABLANCA")
    print("="*80)
    
    # Charger les données finales
    df = pd.read_csv("points_vente_casablanca_zones_corrigees.csv")
    
    print(f"\n📊 STATISTIQUES GÉNÉRALES")
    print("-" * 40)
    print(f"Total des points de vente collectés: {len(df)}")
    print(f"Zone géographique couverte: Casablanca et périphérie")
    print(f"Sources de données: OpenStreetMap (OSM)")
    
    # Répartition par statut
    print(f"\n🏢 RÉPARTITION PAR STATUT")
    print("-" * 40)
    statut_stats = df['Statut'].value_counts()
    for statut, count in statut_stats.items():
        percentage = count / len(df) * 100
        print(f"{statut}: {count:,} points ({percentage:.1f}%)")
    
    # Répartition par catégorie
    print(f"\n🏪 RÉPARTITION PAR CATÉGORIE")
    print("-" * 40)
    category_stats = df['Catégorie'].value_counts()
    for category, count in category_stats.items():
        percentage = count / len(df) * 100
        print(f"{category}: {count:,} points ({percentage:.1f}%)")
    
    # Top 15 des zones
    print(f"\n🗺️ TOP 15 DES ZONES LES PLUS DENSES")
    print("-" * 40)
    zone_stats = df['Zone'].value_counts().head(15)
    for zone, count in zone_stats.items():
        percentage = count / len(df) * 100
        print(f"{zone}: {count:,} points ({percentage:.1f}%)")
    
    # Analyse secteur formel vs informel par zone
    print(f"\n📈 ANALYSE FORMEL/INFORMEL PAR ZONE (TOP 10)")
    print("-" * 40)
    top_zones = df['Zone'].value_counts().head(10).index
    
    for zone in top_zones:
        zone_df = df[df['Zone'] == zone]
        formel = len(zone_df[zone_df['Statut'] == 'Formel'])
        informel = len(zone_df[zone_df['Statut'] == 'Informel'])
        total = len(zone_df)
        
        formel_pct = formel / total * 100 if total > 0 else 0
        informel_pct = informel / total * 100 if total > 0 else 0
        
        print(f"{zone}: {total} points")
        print(f"  └─ Formel: {formel} ({formel_pct:.1f}%) | Informel: {informel} ({informel_pct:.1f}%)")
    
    # Fichiers générés
    print(f"\n📁 FICHIERS GÉNÉRÉS")
    print("-" * 40)
    
    files_generated = [
        ("points_vente_casablanca_zones_corrigees.csv", "Données finales avec zones corrigées"),
        ("casablanca_carte_zones_corrigees.html", "Carte interactive par zones"),
        ("points_vente_casablanca_complet.csv", "Données brutes complètes"),
        ("casablanca_points_vente_complet.html", "Carte complète avec clusters")
    ]
    
    for filename, description in files_generated:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # En KB
            print(f"✅ {filename}")
            print(f"   {description} ({size:.1f} KB)")
        else:
            print(f"❌ {filename} - Non trouvé")
    
    print(f"\n🎯 RECOMMANDATIONS D'UTILISATION")
    print("-" * 40)
    print("• Utilisez 'points_vente_casablanca_zones_corrigees.csv' pour les analyses")
    print("• Ouvrez 'casablanca_carte_zones_corrigees.html' pour la visualisation")
    print("• Les données proviennent d'OpenStreetMap (source fiable)")
    print("• Mise à jour recommandée tous les 3-6 mois")
    
    # Créer un fichier Excel avec plusieurs onglets
    try:
        with pd.ExcelWriter('analyse_points_vente_casablanca.xlsx', engine='openpyxl') as writer:
            # Données complètes
            df.to_excel(writer, sheet_name='Données Complètes', index=False)
            
            # Statistiques par zone
            zone_summary = df.groupby('Zone').agg({
                'Nom': 'count',
                'Statut': lambda x: (x == 'Formel').sum(),
                'Catégorie': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'
            }).rename(columns={
                'Nom': 'Total_Points',
                'Statut': 'Points_Formels',
                'Catégorie': 'Catégorie_Dominante'
            })
            zone_summary['Points_Informels'] = zone_summary['Total_Points'] - zone_summary['Points_Formels']
            zone_summary['Pourcentage_Formel'] = (zone_summary['Points_Formels'] / zone_summary['Total_Points'] * 100).round(1)
            
            zone_summary.to_excel(writer, sheet_name='Résumé par Zone')
            
            # Statistiques par catégorie
            category_summary = df.groupby(['Catégorie', 'Statut']).size().unstack(fill_value=0)
            category_summary.to_excel(writer, sheet_name='Résumé par Catégorie')
        
        print(f"\n✅ Fichier Excel créé: analyse_points_vente_casablanca.xlsx")
        
    except Exception as e:
        print(f"\n❌ Erreur création Excel: {e}")
    
    print(f"\n{'='*80}")
    print("PROJET TERMINÉ AVEC SUCCÈS ! 🎉")
    print("="*80)

if __name__ == "__main__":
    generate_final_summary()