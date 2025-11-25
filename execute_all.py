#!/usr/bin/env python3
"""
Script principal pour collecter et fusionner les données de points de vente à Casablanca
"""

import subprocess
import sys
import os
import time

def run_script(script_name, description):
    """Exécute un script Python avec gestion d'erreurs"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.getcwd())
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ Messages d'erreur:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {script_name} exécuté avec succès!")
            return True
        else:
            print(f"❌ Erreur dans {script_name} (code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏪 SYSTÈME DE COLLECTE DES POINTS DE VENTE - CASABLANCA")
    print("=" * 65)
    
    start_time = time.time()
    
    # Liste des scripts à exécuter
    scripts = [
        ("atp_scraper.py", "Génération des données ATP (AllThePlaces simulé)"),
        ("osm_scraper.py", "Collecte des données OpenStreetMap"),
        ("fusion_data.py", "Fusion des données OSM et ATP"),
        ("merge_data.py", "Fusion complète de toutes les données"),
        ("create_final_map.py", "Génération de la carte interactive")
    ]
    
    success_count = 0
    
    for script, description in scripts:
        if os.path.exists(script):
            if run_script(script, description):
                success_count += 1
                time.sleep(2)  # Pause entre les scripts
            else:
                print(f"⚠️ Continuation malgré l'erreur dans {script}")
        else:
            print(f"❌ Script {script} non trouvé")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DE L'EXÉCUTION")
    print(f"{'='*60}")
    print(f"Scripts exécutés avec succès: {success_count}/{len(scripts)}")
    print(f"Temps total d'exécution: {time.time() - start_time:.1f} secondes")
    
    # Vérifier les fichiers générés
    output_files = [
        "points_vente_casablanca_atp.csv",
        "points_vente_casablanca_osm_new.csv", 
        "points_vente_casablanca_final.csv",
        "points_vente_casablanca_merged.csv",
        "points_vente_casablanca_map.html"
    ]
    
    print(f"\n📁 Fichiers générés:")
    for file in output_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size} bytes)")
        else:
            # Chercher des variants avec timestamp
            import glob
            variants = glob.glob(file.replace('.csv', '_*.csv'))
            if variants:
                latest = max(variants, key=os.path.getctime)
                size = os.path.getsize(latest)
                print(f"   ✅ {latest} ({size} bytes)")
            else:
                print(f"   ❌ {file} non trouvé")
    
    print(f"\n🎉 Processus terminé!")

if __name__ == "__main__":
    main()