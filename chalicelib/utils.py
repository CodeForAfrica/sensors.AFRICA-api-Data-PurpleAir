from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="sensors-api")

def address_converter(lat_long):
    location = geolocator.reverse(lat_long)
    location.raw['address'].update({"display_name": location.address})
    return location.raw['address']
