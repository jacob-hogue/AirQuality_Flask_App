import asyncio
import aiohttp
import json

# API key and base URL setup
api_key = "aa357e82dcb64fe4f6e9ddefc316d5dba8e68c09979e24115f1446854bc8cdc9"
base_location_url = "https://api.openaq.org/v3/locations"
base_sensor_url = "https://api.openaq.org/v3/sensors"

# Define city names and corresponding location IDs
locations = {
    "Bakersfield, CA": [230814, 269725, 28777, 8473],
    "Visalia, CA": [3019000],
    "Fresno, CA": [895, 921008, 234614, 792],
    "Madera, CA": [8457],
    "Hanford, CA": [663]
}

# Function to fetch location data for each location_id
async def fetch_location_data(session, location_id):
    url = f"{base_location_url}/{location_id}"
    async with session.get(url, headers={"X-API-Key": api_key}) as response:
        if response.status == 200:
            location_data = await response.json()
            return location_data
        else:
            print(f"Failed to fetch data for location ID {location_id}. Status code: {response.status}")
            return None

# Function to fetch sensor data for each sensor_id
async def fetch_sensor_data(session, sensor_id):
    url = f"{base_sensor_url}/{sensor_id}"
    async with session.get(url, headers={"X-API-Key": api_key}) as response:
        if response.status == 200:
            sensor_data = await response.json()
            return sensor_data
        else:
            print(f"Failed to fetch data for sensor ID {sensor_id}. Status code: {response.status}")
            return None
        

# Function to convert sensor data to GeoJSON
def convert_to_geojson(sensor_data):
    geojson_features = []

    for sensor_id, sensor_info in sensor_data.items():
        for result in sensor_info.get('results', []):
            # Extracting latitude and longitude
            if 'latest' in result and 'coordinates' in result['latest']:
                latitude = result['latest']['coordinates']['latitude']
                longitude = result['latest']['coordinates']['longitude']
                value = result['latest']['value']
                name = result['name']

                # Extracting parameters, coverage, and summary at the top level
                parameter = result['parameter']
                coverage = result['coverage']
                summary = result['summary']

                # Creating GeoJSON feature
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "properties": {
                        "sensor_id": sensor_id,
                        "sensor_name": name,
                        "latest_value": value,
                        "datetime": result['latest']['datetime']['utc'],
                        # Place parameters at the top level
                        "parameter_id": parameter['id'],
                        "parameter_name": parameter['name'],
                        "parameter_units": parameter['units'],
                        "parameter_displayName": parameter['displayName'],
                        # Place coverage at the top level
                        "coverage_expectedCount": coverage['expectedCount'],
                        "coverage_expectedInterval": coverage['expectedInterval'],
                        "coverage_observedCount": coverage['observedCount'],
                        "coverage_observedInterval": coverage['observedInterval'],
                        "coverage_percentComplete": coverage['percentComplete'],
                        "coverage_percentCoverage": coverage['percentCoverage'],
                        "coverage_datetimeFrom": coverage['datetimeFrom']['utc'],
                        "coverage_datetimeTo": coverage['datetimeTo']['utc'],
                        # Place summary at the top level
                        "summary_min": summary['min'],
                        "summary_max": summary['max'],
                        "summary_avg": summary['avg'],
                        "summary_sd": summary['sd']
                    }
                }
                geojson_features.append(feature)

    # Creating the GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    
    return geojson

def convert_location_to_geojson(location_data):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Iterate over the list of location objects
    for location in location_data:
        # Extract the location id and location info
        for location_id, location_info in location.items():  # Unpack the inner dictionary

            # Extract necessary fields
            result = location_info['results'][0]  # Assuming there's only one result per location
            coordinates = result['coordinates']
            
            # Create a GeoJSON feature
            feature = {
                "type": "Feature",
                "properties": {
                    "id": result["id"],
                    "name": result["name"],
                    "locality": result["locality"],
                    "timezone": result["timezone"],
                    "country": result["country"]["name"],
                    "provider": result["provider"]["name"],
                    "isMobile": result["isMobile"],
                    "isMonitor": result["isMonitor"],
                    "instruments": [instrument["name"] for instrument in result["instruments"]],
                    "sensors": [sensor["name"] for sensor in result["sensors"]],
                    "datetimeFirst": result["datetimeFirst"]["utc"],
                    "datetimeLast": result["datetimeLast"]["utc"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [coordinates["longitude"], coordinates["latitude"]]
                }
            }

            # Add the feature to the features list
            geojson["features"].append(feature)

    return geojson


# Main function to query all locations and print/save JSON responses
async def main():
    output_data = []  # List to hold all location data for saving
    sensors_info = []  # List to hold sensor information

    async with aiohttp.ClientSession() as session:
        for city, location_ids in locations.items():
            for location_id in location_ids:
                data = await fetch_location_data(session, location_id)
                if data:
                    # Print the full JSON response for each location_id
                    print(f"\nJSON Response for Location ID {location_id}:")
                    print(json.dumps(data, indent=4))  # Pretty-print JSON data

                    # Append the JSON response to the output data list
                    output_data.append({location_id: data})

                    # Extract sensor data
                    for result in data.get("results", []):
                        sensors = result.get("sensors", [])
                        for sensor in sensors:
                            sensor_id = sensor["id"]
                            sensor_name = sensor["name"]
                            sensors_info.append({"sensor_id": sensor_id, "sensor_name": sensor_name})
                            print(f"Sensor ID: {sensor_id}, Sensor Name: {sensor_name}")

    # Save the full JSON responses to a file
    with open('DataProcessing\location_responses.json', 'w') as f:
        json.dump(output_data, f, indent=4)

    # Fetch data for each sensor
    sensor_responses = {}
    async with aiohttp.ClientSession() as session:
        sensor_tasks = [fetch_sensor_data(session, sensor['sensor_id']) for sensor in sensors_info]
        sensor_responses_list = await asyncio.gather(*sensor_tasks)

        # Store valid sensor responses
        for sensor_response in sensor_responses_list:
            if sensor_response:
                sensor_id = sensor_response['results'][0]['id'] if sensor_response['results'] else None  # Adjust based on the structure of response
                if sensor_id:  # Check if sensor_id is valid
                    sensor_responses[sensor_id] = sensor_response
                    print(f"Successfully retrieved data for Sensor ID: {sensor_id}")

    # Optionally, save the sensor responses to a JSON file
    with open('DataProcessing\sensor_responses.json', 'w') as outfile:
        json.dump(sensor_responses, outfile, indent=4)

    print("All sensor responses have been saved to sensor_responses.json.")

    # Convert the sensor response to GeoJSON
    geojson_output = convert_to_geojson(sensor_responses)

    # Save the GeoJSON to a file
    with open('DataProcessing\sensor_data.geojson', 'w') as geojson_file:
        json.dump(geojson_output, geojson_file, indent=4)


    # Print the GeoJSON output
    print("GeoJSON Output:")
    print(json.dumps(geojson_output, indent=4))

 

# Load the location responses from the JSON file
with open('DataProcessing\location_responses.json', 'r') as file:
    location_data = json.load(file)

# Convert the JSON data to GeoJSON using the provided function
geojson_data = convert_location_to_geojson(location_data)

# Optionally, save the GeoJSON output to a new file
with open('DataProcessing\locations.geojson', 'w') as geojson_file:
    json.dump(geojson_data, geojson_file, indent=4)

print("GeoJSON conversion complete and saved to 'locations.geojson'.")

# Run the main async function
asyncio.run(main())
