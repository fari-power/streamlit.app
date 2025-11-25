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

# --- Catégories ---
categories = {
    "supermarket": ("Supermarché", "Formel"),
    "convenience": ("Supérette / Mini-market", "Formel"),
    "greengrocer": ("Épicerie", "Informel"),
    "cafe": ("Café", "Formel"),
    "restaurant": ("Restaurant", "Formel"),
    "wholesale": ("Grossiste / Distributeur régional", "Formel"),
    "kiosk": ("Kiosque", "Informel"),
    "bakery": ("Boulangerie", "Formel"),
    "pharmacy": ("Parapharmacie", "Formel"),
    "confectionery": ("Boutique de confiserie", "Informel"),
    "organic": ("Magasin bio", "Formel"),
}

# --- Liste des marques/enseignes alimentaires au Maroc (test réduit) ---
brands = [
    "Carrefour", "Marjane", "McDonald's", "KFC"
]

# --- Fonctions pour OpenStreetMap ---
def query_overpass_api(query):
    """Effectue une requête vers l'API Overpass d'OpenStreetMap"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[WARNING] Erreur API Overpass: {e}")
        return None

def get_brand_data(brand_name, bbox="33.4,-7.8,33.7,-7.4"):
    """Recherche les points de vente d'une marque dans Casablanca"""
    # Bounding box pour Casablanca (approximative)
    query = f"""
    [out:json][timeout:25];
    (
      node["name"~"{brand_name}",i]({bbox});
      way["name"~"{brand_name}",i]({bbox});
      relation["name"~"{brand_name}",i]({bbox});
    );
    out center;
    """
    
    return query_overpass_api(query)

data_list = []

for brand in brands:
    print(f"[INFO] Collecte des points pour {brand}...")
    try:
        osm_data = get_brand_data(brand)
        if not osm_data or 'elements' not in osm_data:
            print(f"   Aucune donnée trouvée pour {brand}")
            continue
            
        for element in osm_data['elements']:
            if 'tags' not in element:
                continue
                
            name = element['tags'].get('name', brand)
            
            # Obtenir les coordonnées selon le type d'élément
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
                
            zone = get_zone(lat, lon)
            
            # Déterminer la catégorie basée sur les tags OSM
            shop_type = element['tags'].get('shop', '')
            amenity_type = element['tags'].get('amenity', '')
            
            category = "supermarket"  # par défaut
            if shop_type in ["supermarket", "hypermarket"]:
                category = "supermarket"
            elif shop_type in ["convenience", "general"]:
                category = "convenience"
            elif shop_type in ["greengrocer", "organic"]:
                category = "greengrocer"
            elif amenity_type in ["cafe", "restaurant", "fast_food"]:
                if amenity_type == "cafe":
                    category = "cafe"
                else:
                    category = "restaurant"
            elif shop_type == "bakery":
                category = "bakery"
            elif shop_type == "chemist":
                category = "pharmacy"
                
            cat, statut = categories.get(category, ("Supermarché", "Formel"))
            image = images.get(cat, "Aucune image")
            
            address = element['tags'].get('addr:full') or element['tags'].get('addr:street', name)
            
            data_list.append({
                "Zone": zone,
                "Nom": name,
                "Catégorie": cat,
                "Statut": statut,
                "Adresse": address,
                "Latitude": lat,
                "Longitude": lon,
                "Image": image
            })
            
        time.sleep(5)  # Pause plus longue pour respecter l'API
        
    except Exception as e:
        print(f"[WARNING] Erreur pour {brand}: {e}")

# --- CSV final ---
if data_list:
    df = pd.DataFrame(data_list)
    df.drop_duplicates(subset=["Nom", "Latitude", "Longitude"], inplace=True)
    
    # Utiliser un nom de fichier différent s'il y a un conflit
    output_file = "points_vente_casablanca_osm_new.csv"
    try:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] CSV enregistre ({len(df)} points) dans {output_file}")
    except PermissionError:
        output_file = f"points_vente_casablanca_osm_{int(time.time())}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] CSV enregistre ({len(df)} points) dans {output_file}")
else:
    print("[ERROR] Aucune donnee collectee")
