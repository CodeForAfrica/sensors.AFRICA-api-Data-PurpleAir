import requests
from .settings import (PURPLE_AIR_API, PURPLE_AIR_API_KEY,
                        SENSORS_AFRICA_API, SENSORS_AFRICA_API_KEY, 
                        OWNER_ID, )
from .utils import address_converter

def run():
    url = f"{PURPLE_AIR_API}/sensors?api_key={PURPLE_AIR_API_KEY}&fields=name,location_type,latitude,longitude,altitude,humidity,temperature,pressure,voc,ozone1,analog_input"
    response = requests.get(url)
    fields = []
    data = []
    if response.ok:
        json_response = response.json()
        fields = json_response['fields']
        sensors = json_response['data']

    """
    From the docs, fields is
    An array of values representing the headers for the "data"
    field and describe the meanings of the columns in the data field.
    For example, fields[column] is the header for data[row][column]. 
    You should always identify the data column index by looking for the desired header
    in the fields array since the column order is not guaranteed to always stay the same.
    """
    for index, row_data in enumerate(sensors):
        sensors[index] = dict(zip(fields, row_data))
    
    nodes = get_sensors_africa_nodes()
    for sensor in sensors:
        if sensor['sensor_index'] not in nodes:
            # Create Location
            address = address_converter(sensor['longitude'], sensor['latitude'])
            location = create_location({"location": address['display_name'],
                            "longitude": sensor.get('longitude'),
                            "latitude": sensor.get('latitude'),
                            "altitude": sensor.get('altitude'),
                            "country": address.get('country'),
                            "postalcode": address.get('postcode'),
                            })
            if location:
                # Create the Node
                create_node(node={"uid": sensor['sensor_index'], 'owner': OWNER_ID, 'location': location})

def get_sensors_africa_nodes():
    response = requests.get(f"{SENSORS_AFRICA_API}/nodes/")
    if response.ok:
        return [res['node']['uid'] for res in response.json()]
    return []

def create_node(node):
    response = requests.post(f"{SENSORS_AFRICA_API}/nodes/",
    data=node,
    headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})
    return

def create_location(location):
    response = requests.post(f"{SENSORS_AFRICA_API}/locations/",
    data=location,
    headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})
    if response.ok:
        return response.json()['id']