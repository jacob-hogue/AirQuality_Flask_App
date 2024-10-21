import asyncio
import aiohttp
import json

# API key and base URL setup
api_key = "aa357e82dcb64fe4f6e9ddefc316d5dba8e68c09979e24115f1446854bc8cdc9"

# List of sensor IDs to query
sensors_info = [
    {'sensor_id': 1639},
    {'sensor_id': 24365},
    {'sensor_id': 24551},
    {'sensor_id': 1328938},
    {'sensor_id': 1349599},
    {'sensor_id': 5077547},
    {'sensor_id': 5077593},
    {'sensor_id': 10280894}
]

# Function to fetch sensor data for each sensor_id
async def fetch_sensor_data(session, sensor_id):
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days/yearly?limit=10"
    async with session.get(url, headers={"X-API-Key": api_key}) as response:
        if response.status == 200:
            sensor_data = await response.json()
            # Append sensor_id to the data
            sensor_data['sensor_id'] = sensor_id
            print(f"Fetched data for Sensor ID {sensor_id}: {sensor_data}")  # Debugging line
            return sensor_data
        else:
            print(f"Failed to fetch data for sensor ID {sensor_id}. Status code: {response.status}")
            return None

async def main():
    # Fetch data for each sensor
    all_sensor_data = []
    async with aiohttp.ClientSession() as session:
        sensor_tasks = [fetch_sensor_data(session, sensor['sensor_id']) for sensor in sensors_info]
        sensor_responses_list = await asyncio.gather(*sensor_tasks)

        # Store valid sensor responses
        for sensor_response in sensor_responses_list:
            if sensor_response:
                all_sensor_data.append(sensor_response)  # Append the response to the list

    # Save all sensor data to a JSON file
    with open('DataProcessing/sensor_data_historical.json', 'w') as outfile:
        json.dump(all_sensor_data, outfile, indent=4)
        print("All sensor data has been saved to DataProcessing/sensor_data_historical.json.")

# Run the main function
asyncio.run(main())



import json
import csv

# Read the JSON file
with open('DataProcessing/sensor_data_historical.json', 'r') as f:
    data = json.load(f)

# Open a CSV file for writing
with open('sensor_data_historical.csv', 'w', newline='') as csvfile:
    fieldnames = ['sensor_id', 'period_from', 'period_to', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write the data
    for item in data:
        for result in item['results']:
            writer.writerow({
                'sensor_id': item['sensor_id'],
                'period_from': result['period']['datetimeFrom']['utc'],
                'period_to': result['period']['datetimeTo']['utc'],
                'value': result['value']
            })

print("Data has been successfully written to sensor_data_historical.csv")
