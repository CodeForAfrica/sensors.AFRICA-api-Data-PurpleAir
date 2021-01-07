import json
from .settings import OWNER_ID
from .utils import address_converter
from chalicelib.sensorafrica import (
    get_sensors_africa_nodes,
    get_sensors_africa_locations,
    get_sensors_africa_sensor_types,
    get_purple_air_sensor,
    create_sensor_type,
    create_node,
    create_location,
    create_sensor,
    send_sensor_data,
)


def get_sensors():
    with open("chalicelib/sensors.json") as data:
        sensors = json.load(data)
        return [sensor["ID"] for sensor in sensors]
    return []


def run():
    sensors = get_sensors()
    nodes = get_sensors_africa_nodes()
    locations = get_sensors_africa_locations()
    sensor_types = get_sensors_africa_sensor_types()

    for sensor in sensors:
        # Get data for every sensor we want to monitor
        try:
            sensor_data = get_purple_air_sensor(sensor)
        except Exception:
            continue
        if str(sensor_data["sensor_index"]) not in [
            node["uid"] for node in nodes if node
        ]:
            lat_log = f"{round(sensor_data['latitude'], 3)},\
                        {round(sensor_data['longitude'], 3)}"
            address = address_converter(lat_log)

            location = [loc.get(lat_log) for loc in locations if loc.get(lat_log)]

            if location:
                location = location[0]
            else:
                # Create Location
                location = create_location(
                    {
                        "location": address["display_name"],
                        "longitude": sensor_data.get("longitude"),
                        "latitude": sensor_data.get("latitude"),
                        "altitude": sensor_data.get("altitude"),
                        "owner": OWNER_ID,
                        "country": address.get("country"),
                        "city": address.get("city"),
                        "postalcode": address.get("postcode"),
                    }
                )

            node_id = create_node(
                node={
                    "uid": sensor_data["sensor_index"],
                    "owner": OWNER_ID,
                    "location": location,
                }
            )
        else:
            node_id = [
                node["id"]
                for node in nodes
                if node["uid"] == str(sensor_data["sensor_index"])
            ]
            if node_id:
                node_id = node_id[0]

        if not node_id:
            # This should not happen
            continue

        if sensor_types:
            if [
                sensor_data["model"] in sensor_type.keys()
                for sensor_type in sensor_types
            ][0]:
                sensor_type = [
                    st.get(sensor_data["model"])
                    for st in sensor_types
                    if st.get(sensor_data["model"])
                ][0]
            else:
                # Create sensor-type
                sensor_type = create_sensor_type(sensor_data)
        else:
            # Create sensor-type
            sensor_type = create_sensor_type(sensor_data)
        # Create sensor
        create_sensor({"node": node_id, "sensor_type": sensor_type})

        # Send sensor Data
        send_sensor_data(sensor_data["sensor_index"], sensor_data)
