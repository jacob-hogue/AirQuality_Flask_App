import geopandas as gpd
from sqlalchemy import create_engine
from datetime import datetime

# Database configuration
db_config = {
    "user": "postgres",      # Replace with your username
    "password": "postgres",  # Replace with your password
    "host": "localhost",     # Change if your database is hosted elsewhere
    "port": "5432",          # Default PostgreSQL port
    "database": "AirQuality" # Replace with your database name
}

# Create a connection string
connection_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(connection_string)

# Load the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file("DataProcessing\sensor_data.geojson")

# Filter the GeoDataFrame by 'sensor_name'
filtered_gdf = gdf[gdf['sensor_name'] == 'pm25 µg/m³']

# Extract latitude and longitude from the geometry
filtered_gdf['lon'] = filtered_gdf.geometry.x
filtered_gdf['lat'] = filtered_gdf.geometry.y

# Append today's date to the 'Date_Added' column
today = datetime.now().date()
filtered_gdf['Date_Added'] = today

# Specify the table name
table_name = "sensor_data"  # Change to your desired table name

# Save the GeoDataFrame to the PostgreSQL database
filtered_gdf.to_postgis(table_name, engine, if_exists='append', index=False)

print(f"GeoJSON data loaded into table '{table_name}' in the database '{db_config['database']}' successfully.")

# Load the Locations GeoJSON file into a GeoDataFrame
locations_gdf = gpd.read_file("DataProcessing\locations.geojson")

# Extract latitude and longitude from the geometry for locations_data
locations_gdf['lon'] = locations_gdf.geometry.x
locations_gdf['lat'] = locations_gdf.geometry.y

# Specify the table name
locations_table_name = "locations_data"  # Change to your desired table name

# Save the GeoDataFrame to the PostgreSQL database
locations_gdf.to_postgis(locations_table_name, engine, if_exists='replace', index=False)

print(f"GeoJSON data loaded into table '{locations_table_name}' in the database '{db_config['database']}' successfully.")
