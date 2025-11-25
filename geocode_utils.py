from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="points_vente_casablanca")

def get_zone(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="fr", exactly_one=True)
        if location and 'suburb' in location.raw['address']:
            return location.raw['address']['suburb']
        elif location and 'city' in location.raw['address']:
            return location.raw['address']['city']
        else:
            return "N/A"
    except Exception as e:
        print(f"⚠️ Erreur géocodage pour {lat}, {lon}: {e}")
        return "N/A"
