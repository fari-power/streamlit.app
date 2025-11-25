import pandas as pd
import time
import os
import requests
from geocode_utils import get_zone

# --- Icônes ---
os.makedirs("icons", exist_ok=True)
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

def query_overpass_api(query):
    """Effectue une requête vers l'API Overpass d'OpenStreetMap"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[WARNING] Erreur API Overpass: {e}")
        return None

def get_all_food_retail_casablanca():
    """Recherche TOUS les commerces alimentaires dans la région de Casablanca"""
    
    # Bounding box élargie pour couvrir toute l'agglomération de Casablanca
    # Sud-Ouest: 33.4, -7.9 | Nord-Est: 33.7, -7.3
    bbox = "33.4,-7.9,33.7,-7.3"
    
    print(f"[INFO] Recherche dans la zone: {bbox}")
    
    # Requête pour tous les types de commerces alimentaires
    query = f"""
    [out:json][timeout:120];
    (
      // Supermarchés et grandes surfaces
      node["shop"="supermarket"]({bbox});
      way["shop"="supermarket"]({bbox});
      relation["shop"="supermarket"]({bbox});
      
      // Magasins de proximité
      node["shop"="convenience"]({bbox});
      way["shop"="convenience"]({bbox});
      relation["shop"="convenience"]({bbox});
      
      // Épiceries
      node["shop"="general"]({bbox});
      way["shop"="general"]({bbox});
      relation["shop"="general"]({bbox});
      
      node["shop"="greengrocer"]({bbox});
      way["shop"="greengrocer"]({bbox});
      relation["shop"="greengrocer"]({bbox});
      
      // Boulangeries
      node["shop"="bakery"]({bbox});
      way["shop"="bakery"]({bbox});
      relation["shop"="bakery"]({bbox});
      
      // Parapharmacies
      node["shop"="chemist"]({bbox});
      way["shop"="chemist"]({bbox});
      relation["shop"="chemist"]({bbox});
      
      // Pharmacies
      node["amenity"="pharmacy"]({bbox});
      way["amenity"="pharmacy"]({bbox});
      relation["amenity"="pharmacy"]({bbox});
      
      // Cafés
      node["amenity"="cafe"]({bbox});
      way["amenity"="cafe"]({bbox});
      relation["amenity"="cafe"]({bbox});
      
      // Restaurants
      node["amenity"="restaurant"]({bbox});
      way["amenity"="restaurant"]({bbox});
      relation["amenity"="restaurant"]({bbox});
      
      // Fast food
      node["amenity"="fast_food"]({bbox});
      way["amenity"="fast_food"]({bbox});
      relation["amenity"="fast_food"]({bbox});
      
      // Kiosques
      node["shop"="kiosk"]({bbox});
      way["shop"="kiosk"]({bbox});
      relation["shop"="kiosk"]({bbox});
      
      // Magasins bio
      node["shop"="organic"]({bbox});
      way["shop"="organic"]({bbox});
      relation["shop"="organic"]({bbox});
      
      // Confiseries
      node["shop"="confectionery"]({bbox});
      way["shop"="confectionery"]({bbox});
      relation["shop"="confectionery"]({bbox});
      
      // Marchés
      node["amenity"="marketplace"]({bbox});
      way["amenity"="marketplace"]({bbox});
      relation["amenity"="marketplace"]({bbox});
    );
    out center;
    """
    
    return query_overpass_api(query)

def categorize_point(element):
    """Détermine la catégorie et le statut d'un point de vente"""
    
    if 'tags' not in element:
        return None, None
    
    tags = element['tags']
    shop_type = tags.get('shop', '')
    amenity_type = tags.get('amenity', '')
    
    # Mapping des catégories OSM vers nos catégories
    category_mapping = {
        # Formel - Grandes surfaces
        'supermarket': ("Supermarché", "Formel"),
        'convenience': ("Supérette / Mini-market", "Formel"),
        
        # Informel - Commerces traditionnels
        'general': ("Épicerie", "Informel"),
        'greengrocer': ("Épicerie", "Informel"),
        'kiosk': ("Kiosque", "Informel"),
        'confectionery': ("Boutique de confiserie", "Informel"),
        
        # Formel - Services
        'bakery': ("Boulangerie", "Formel"),
        'chemist': ("Parapharmacie", "Formel"),
        'organic': ("Magasin bio", "Formel"),
    }
    
    amenity_mapping = {
        'pharmacy': ("Parapharmacie", "Formel"),
        'cafe': ("Café", "Formel"),
        'restaurant': ("Restaurant", "Formel"),
        'fast_food': ("Restaurant", "Formel"),
        'marketplace': ("Épicerie", "Informel"),
    }
    
    # Déterminer la catégorie
    if shop_type in category_mapping:
        return category_mapping[shop_type]
    elif amenity_type in amenity_mapping:
        return amenity_mapping[amenity_type]
    else:
        # Catégorie par défaut
        return ("Épicerie", "Informel")

def main():
    """Fonction principale"""
    
    print("="*70)
    print("COLLECTE COMPLETE DES POINTS DE VENTE - CASABLANCA")
    print("="*70)
    
    print("[INFO] Debut de la collecte OSM pour toute la region de Casablanca...")
    
    # Collecter toutes les données
    osm_data = get_all_food_retail_casablanca()
    
    if not osm_data or 'elements' not in osm_data:
        print("[ERROR] Aucune donnee OSM collectee")
        return
    
    print(f"[INFO] {len(osm_data['elements'])} elements bruts collectes")
    
    data_list = []
    processed_count = 0
    
    for element in osm_data['elements']:
        if 'tags' not in element:
            continue
        
        # Obtenir les coordonnées
        if element['type'] == 'node':
            lat = element.get('lat')
            lon = element.get('lon')
        elif element['type'] in ['way', 'relation'] and 'center' in element:
            lat = element['center'].get('lat')
            lon = element['center'].get('lon')
        else:
            continue
        
        if not lat or not lon:
            continue
        
        # Catégoriser le point
        category_info = categorize_point(element)
        if not category_info[0]:
            continue
        
        category, statut = category_info
        
        # Obtenir le nom
        name = element['tags'].get('name', f"{category} sans nom")
        
        # Obtenir l'adresse
        address_parts = []
        for addr_key in ['addr:full', 'addr:street', 'addr:city']:
            if addr_key in element['tags']:
                address_parts.append(element['tags'][addr_key])
        
        address = ', '.join(address_parts) if address_parts else name
        
        # Obtenir la zone (sans limitation de zone spécifique)
        try:
            zone = get_zone(lat, lon) if get_zone else "Casablanca"
        except:
            zone = "Casablanca"
        
        # Obtenir l'icône
        image = images.get(category, "icons/supermarket.png")
        
        data_list.append({
            "Zone": zone,
            "Nom": name,
            "Catégorie": category,
            "Statut": statut,
            "Adresse": address,
            "Latitude": lat,
            "Longitude": lon,
            "Image": image
        })
        
        processed_count += 1
        
        # Afficher le progrès
        if processed_count % 100 == 0:
            print(f"[INFO] {processed_count} points traites...")
    
    print(f"[INFO] {processed_count} points valides traites")
    
    if not data_list:
        print("[ERROR] Aucun point de vente valide trouve")
        return
    
    # Créer le DataFrame et nettoyer
    df = pd.DataFrame(data_list)
    initial_count = len(df)
    
    # Supprimer les doublons
    df = df.drop_duplicates(subset=["Nom", "Latitude", "Longitude"], keep='first')
    final_count = len(df)
    
    print(f"[INFO] {initial_count - final_count} doublons supprimes")
    
    # Statistiques par catégorie
    print(f"\n[INFO] Repartition par categorie:")
    category_stats = df['Catégorie'].value_counts()
    for category, count in category_stats.items():
        print(f"   {category}: {count}")
    
    # Statistiques par statut
    print(f"\n[INFO] Repartition par statut:")
    status_stats = df['Statut'].value_counts()
    for status, count in status_stats.items():
        print(f"   {status}: {count}")
    
    # Sauvegarder
    output_file = "points_vente_casablanca_complet.csv"
    try:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[SUCCESS] {final_count} points de vente sauvegardes dans {output_file}")
    except PermissionError:
        output_file = f"points_vente_casablanca_complet_{int(time.time())}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[SUCCESS] {final_count} points de vente sauvegardes dans {output_file}")

if __name__ == "__main__":
    main()