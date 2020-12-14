from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="sensors-api")

def address_converter(longitude, latitude):
    location = geolocator.reverse(f"{latitude}, {longitude}")
    location.raw['address'].update({"display_name": location.address})
    return location.raw['address']
