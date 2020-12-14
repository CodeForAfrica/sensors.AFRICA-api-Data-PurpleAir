import requests
from .settings import (PURPLE_AIR_API, PURPLE_AIR_API_KEY,
                        SENSORS_AFRICA_API, SENSORS_AFRICA_API_KEY, 
                        OWNER_ID, )
from .utils import address_converter

def run():
    response = get_purple_air_sensors()
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
    locations = get_sensors_africa_locations()
    
    for sensor in sensors[:10]:
        if sensor['sensor_index'] not in nodes:
            lat_log = f"{round(sensor['latitude'], 3)}, {round(sensor['longitude'], 3)}"
            address = address_converter(lat_log)

            location = [loc.get(lat_log) for loc in locations if loc.get(lat_log)]
            
            if location:
                location = location[0]
            else:
                # Create Location
                location = create_location({"location": address['display_name'],
                                "longitude": sensor.get('longitude'),
                                "latitude": sensor.get('latitude'),
                                "altitude": sensor.get('altitude'),
                                "country": address.get('country'),
                                "postalcode": address.get('postcode'),
                                })
            create_node(node={"uid": sensor['sensor_index'], 'owner': OWNER_ID, 'location': location})

            # Create sensor-type
            sensor_type = create_sensor_type(sensor['sensor_index'])

def get_purple_air_sensors():
    url = f"{PURPLE_AIR_API}/sensors?api_key={PURPLE_AIR_API_KEY}&fields=name,location_type,latitude,longitude,altitude,humidity,temperature,pressure,voc,ozone1,analog_input"
    response = requests.get(url)
    return response

def get_sensors_africa_nodes():
    response = requests.get(f"{SENSORS_AFRICA_API}/nodes/")
    if response.ok:
        return [res['node']['uid'] for res in response.json()]
    return []

def get_sensors_africa_locations():
    response = requests.get(f"{SENSORS_AFRICA_API}/locations/", headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})
    if response.ok:
        """
            Using latitude, longitude as a key and location id as value to help us find already existing location latter without having to ping the server
            Using round ensures latitude, longitude value will be the same as lat_log in the run method.
        """
        formated_response = [{f"{round(float(location['latitude']), 3)}, {round(float(location['longitude']), 3)}":
                            f"{location['id']}"} for location in response.json()]

        return formated_response
    return []

def get_purple_air_sensor(sensor_id):
    url = f"{PURPLE_AIR_API}/sensors/{sensor_id}?api_key={PURPLE_AIR_API_KEY}"
    response = requests.get(url)
    if response.ok:
        return response.json()['sensor']

def create_node(node):
    response = requests.post(f"{SENSORS_AFRICA_API}/nodes/",
    data=node,
    headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})

def create_location(location):
    response = requests.post(f"{SENSORS_AFRICA_API}/locations/",
    data=location,
    headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})
    if response.ok:
        return response.json()['id']
    else:
        raise Exception(response.json())

def create_sensor_type(sensor_id):
    sensor = get_purple_air_sensor(sensor_id)
    if sensor:
        data = {"uid": sensor['model'], "name": sensor['model'], "manufacturer": "Purple Air"}
        response = requests.post(f"{SENSORS_AFRICA_API}/sensor-types/",
        data=data,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"})
        if response.ok:
            return response.json()['id']
