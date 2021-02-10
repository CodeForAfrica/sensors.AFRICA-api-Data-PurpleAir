import requests
from datetime import datetime, timezone
    
from .settings import (
    PURPLE_AIR_API,
    PURPLE_AIR_API_KEY,
    SENSORS_AFRICA_API,
    SENSORS_AFRICA_API_KEY,
)


def get_sensors_africa_nodes():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/nodes/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()
    return []


def get_sensors_africa_locations():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/locations/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    locations = []

    if response.ok:
        """
        Using latitude, longitude as a key and location id as value to help us
        find already existing location latter without having to ping the server
        Using round ensures latitude, longitude value will be the same as
        lat_log in the run method.
        """
        for location in response.json():
            loc = {
                f"{round(float(location['latitude']), 3)}, {round(float(location['longitude']), 3)}": f"{location['id']}"
            }
            # loc = f"{round(float(location['latitude']), 3)}, {round(float(location['longitude']), 3)}": f"{location['id']}"
            locations.append(loc)

    return locations


def get_sensors_africa_sensor_types():
    response = requests.get(
        f"{SENSORS_AFRICA_API}/v2/sensor-types/",
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return [
            {f"{sensor_type['uid']}": sensor_type["id"]}
            for sensor_type in response.json()
        ]
    return []


def get_purple_air_sensor(sensor_id):
    url = f"{PURPLE_AIR_API}/sensors/{sensor_id}?api_key={PURPLE_AIR_API_KEY}"
    response = requests.get(url)
    if response.ok:
        return response.json()["sensor"]
    raise Exception(response.text)


def create_node(node):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/nodes/",
        data=node,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]


def create_location(location):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/locations/",
        data=location,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]
    else:
        raise Exception(response.text)


def create_sensor_type(sensor):
    if sensor:
        data = {
            "uid": sensor["model"],
            "name": sensor["model"],
            "manufacturer": "Purple Air",
        }
        response = requests.post(
            f"{SENSORS_AFRICA_API}/v2/sensor-types/",
            data=data,
            headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
        )
        if response.ok:
            return response.json()["id"]


def create_sensor(sensor):
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v2/sensors/",
        data=sensor,
        headers={"Authorization": f"Token {SENSORS_AFRICA_API_KEY}"},
    )
    if response.ok:
        return response.json()["id"]
    else:
        # If failure is because sensor already exists,
        return -1


def send_sensor_data(sensor_id, sensor_data, timestamp):
    timestamp = datetime.fromtimestamp(timestamp, timezone.utc).isoformat('T', 'microseconds')
    
    sensordatavalues = [
        {"value": sensor_data["humidity_a"], "value_type": "humidity"},
            {"value": sensor_data["temperature_a"], "value_type": "temperature"},
            {"value": sensor_data["pm1.0_a"], "value_type": "P1"},
            {"value": sensor_data["pm2.5_a"], "value_type": "P2"},
            {"value": sensor_data["pm10.0_a"], "value_type": "P10"},
    ]
    if sensor_data["pressure_a"]:
        sensordatavalues.append({"value": sensor_data["pressure_a"], "value_type": "pressure"})

    data = {
        "sensordatavalues": sensordatavalues,
        "timestamp": timestamp
    }
    if not timestamp:
        del data['timestamp']
    response = requests.post(
        f"{SENSORS_AFRICA_API}/v1/push-sensor-data/",
        json=data,
        headers={
            "SENSOR": str(sensor_id),
            "Authorization": f"Token {SENSORS_AFRICA_API_KEY}",
        },
    )
    return response.json()
