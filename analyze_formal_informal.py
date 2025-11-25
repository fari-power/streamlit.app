#!/usr/bin/env python3
"""
Analyse des points de vente par statut Formel/Informel
"""

import pandas as pd
import os
from collections import defaultdict

def analyze_formal_informal():
    """Analyse la répartition Formel vs Informel des points de vente"""
    
    print("="*70)
    print("ANALYSE FORMEL vs INFORMEL - POINTS DE VENTE CASABLANCA")
    print("="*70)
    
    # Classification des catégories
    formel_categories = {
        "Supermarché": "Formel",
        "Supérette / Mini-market": "Formel", 
        "Café": "Formel",
        "Restaurant": "Formel",
        "Grossiste / Distributeur régional": "Formel",
        "Boulangerie": "Formel",
        "Parapharmacie": "Formel",
        "Magasin bio": "Formel"
    }
    
    informel_categories = {
        "Épicerie": "Informel",
        "Kiosque": "Informel",
        "Boutique de confiserie": "Informel"
    }
    
    # Combiner toutes les catégories
    all_categories = {**formel_categories, **informel_categories}
    
    # Analyser chaque fichier de données
    files_to_analyze = [
        "points_vente_casablanca.csv",
        "points_vente_casablanca_osm.csv", 
        "points_vente_casablanca_final.csv"
    ]
    
    for filename in files_to_analyze:
        if os.path.exists(filename):
            print(f"\n📁 ANALYSE DE: {filename}")
            print("-" * 50)
            
            try:
                df = pd.read_csv(filename)
                
                if 'Catégorie' not in df.columns:
                    print("   ❌ Colonne 'Catégorie' non trouvée")
                    continue
                
                # Statistiques générales
                total_points = len(df)
                categories_found = df['Catégorie'].value_counts()
                
                print(f"   📊 Total points: {total_points}")
                
                # Calculer Formel vs Informel
                formel_count = 0
                informel_count = 0
                autres_count = 0
                
                formel_details = defaultdict(int)
                informel_details = defaultdict(int)
                autres_details = defaultdict(int)
                
                for category, count in categories_found.items():
                    if category in formel_categories:
                        formel_count += count
                        formel_details[category] = count
                    elif category in informel_categories:
                        informel_count += count
                        informel_details[category] = count
                    else:
                        autres_count += count
                        autres_details[category] = count
                
                # Afficher les résultats
                print(f"\n   🏢 SECTEUR FORMEL: {formel_count} points ({formel_count/total_points*100:.1f}%)")
                for cat, count in sorted(formel_details.items(), key=lambda x: x[1], reverse=True):
                    percentage = count/total_points*100
                    print(f"      • {cat}: {count} ({percentage:.1f}%)")
                
                print(f"\n   🏪 SECTEUR INFORMEL: {informel_count} points ({informel_count/total_points*100:.1f}%)")
                for cat, count in sorted(informel_details.items(), key=lambda x: x[1], reverse=True):
                    percentage = count/total_points*100
                    print(f"      • {cat}: {count} ({percentage:.1f}%)")
                
                if autres_count > 0:
                    print(f"\n   ❓ AUTRES CATÉGORIES: {autres_count} points ({autres_count/total_points*100:.1f}%)")
                    for cat, count in sorted(autres_details.items(), key=lambda x: x[1], reverse=True):
                        percentage = count/total_points*100
                        print(f"      • {cat}: {count} ({percentage:.1f}%)")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
    
    print(f"\n{'='*70}")
    print("CRÉATION D'UN FICHIER AVEC CLASSIFICATION FORMEL/INFORMEL")
    print(f"{'='*70}")
    
    # Créer un fichier avec la classification correcte
    main_file = "points_vente_casablanca_final.csv"
    if os.path.exists(main_file):
        df = pd.read_csv(main_file)
        
        # Ajouter la colonne Statut_Reel basée sur la catégorie
        def get_real_status(category):
            if category in formel_categories:
                return "Formel"
            elif category in informel_categories:
                return "Informel"
            else:
                return "Non classifié"
        
        df['Statut_Reel'] = df['Catégorie'].apply(get_real_status)
        
        # Sauvegarder
        output_file = "points_vente_casablanca_avec_statut.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ Fichier créé: {output_file}")
        print(f"   Colonnes: {', '.join(df.columns.tolist())}")
        
        # Statistiques finales
        statut_counts = df['Statut_Reel'].value_counts()
        print(f"\n📈 RÉSUMÉ FINAL:")
        for statut, count in statut_counts.items():
            percentage = count/len(df)*100
            print(f"   {statut}: {count} points ({percentage:.1f}%)")

def create_formal_informal_map():
    """Crée une carte avec distinction Formel/Informel"""
    
    input_file = "points_vente_casablanca_avec_statut.csv"
    if not os.path.exists(input_file):
        print("❌ Fichier avec statut non trouvé. Exécutez d'abord l'analyse.")
        return
    
    try:
        import folium
        from folium.plugins import MarkerCluster
        
        df = pd.read_csv(input_file)
        
        # Créer la carte centrée sur Casablanca
        casablanca_center = [33.5731, -7.5898]
        m = folium.Map(location=casablanca_center, zoom_start=12)
        
        # Couleurs pour chaque statut
        colors = {
            'Formel': 'blue',
            'Informel': 'red', 
            'Non classifié': 'gray'
        }
        
        # Ajouter les marqueurs par statut
        for statut in ['Formel', 'Informel', 'Non classifié']:
            df_statut = df[df['Statut_Reel'] == statut]
            
            if len(df_statut) > 0:
                cluster = MarkerCluster(name=f"{statut} ({len(df_statut)} points)")
                
                for idx, row in df_statut.iterrows():
                    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                        popup_text = f"""
                        <b>{row['Nom']}</b><br>
                        Catégorie: {row['Catégorie']}<br>
                        Statut: {row['Statut_Reel']}<br>
                        Adresse: {row.get('Adresse', 'N/A')}
                        """
                        
                        folium.Marker(
                            location=[row['Latitude'], row['Longitude']],
                            popup=folium.Popup(popup_text, max_width=300),
                            tooltip=f"{row['Nom']} ({statut})",
                            icon=folium.Icon(color=colors[statut], icon='info-sign')
                        ).add_to(cluster)
                
                cluster.add_to(m)
        
        # Ajouter le contrôle des couches
        folium.LayerControl().add_to(m)
        
        # Ajouter une légende
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Légende</b></p>
        <p><i class="fa fa-circle" style="color:blue"></i> Secteur Formel</p>
        <p><i class="fa fa-circle" style="color:red"></i> Secteur Informel</p>
        <p><i class="fa fa-circle" style="color:gray"></i> Non classifié</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Sauvegarder la carte
        map_file = "points_vente_casablanca_formel_informel.html"
        m.save(map_file)
        
        print(f"✅ Carte créée: {map_file}")
        
    except ImportError:
        print("❌ Folium non installé. Installez avec: pip install folium")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la carte: {e}")

if __name__ == "__main__":
    analyze_formal_informal()
    print("\n" + "="*70)
    print("CRÉATION DE LA CARTE FORMEL/INFORMEL")
    print("="*70)
    create_formal_informal_map()