# AirQuality_Flask_App
Inspiration and reference taken from: Parinda Pannoon
https://github.com/parindapannoon/PostGIS_FetchdataAPI


**[Demo Video for Querying endpoints by sensor_id and city boundary](https://www.loom.com/share/17af9fb154c54e999455c59acf697670?sid=3716a19d-6ab2-4a7c-8522-11dd291c47c3)**

## Data Processing
The Data Processing Directory contains 3 scripts
1. APIQuery.py - Script that gets the location and sensor data from the top 5 most polluted cities in the U.S. in terms of PM 2.5 metrics: Bakersfield, Visalia, Fresno, Madera, and Hanford, CA. Converts the OpenAQ json response to usable geodataframe and geojson data using geopandas.
2. SensorData_to_Postgres.py - Script that loads the sensor and location data into a postgis/postgres database using sqlalchemy.
3. HistoricalDataQuery.py - Script that grabs the last 10 years of data for each sensor and dumps the data to a CSV for use in the Flourish chart/table.

## Requirements
```
Flask==3.0.3   
Flask-SQLAlchemy==3.1.1
GeoAlchemy2==0.15.2
Jinja2==3.1.4
psycopg2==2.9.9
SQLAlchemy==2.0.35
Werkzeug==3.0.4
```

## Set up and create flask environment
**Bash**
```
mkdir AirQuality_FlaskApp  
cd AirQuality_FlaskApp  
python -m venv flaskvenv  
flaskvenv\Scripts\activate  
pip install flask  
type nul>app.py (create a Python file for the Flask app, e.g., app.py:)  
```

## Edit app.py and add the following folders/directory:
1. create a templates folder for app.html
2. create a directory for static files

### Use Python to execute your Flask app
```
python app.py
```
## How to use 
Add connection to your database server 'postgresql://postgres:xxxx@localhost/postgres' is URI that tells Flask how to connect to the PostgreSQL database

``` postgresql ``` Specifies that you’re using the PostgreSQL database system.

```postgres ``` The username for the database.

``` xxxx ``` The password for the postgres user.

``` localhost ``` Specifies that the database server is running locally on your machine.

``` postgres ``` The name of the database being connected to

Define a route that responds to GET requests when a URL with a specific sensor_id or show all sensor points

``` @app.route('/sensor/<int:sensor_id>', methods=['GET']) ```

## Data Source 
Open AQ - Open Air Quality Data

https://openaq.org/

![image](https://github.com/user-attachments/assets/7fe365b5-b2d1-4202-b8f3-4f96e5c14778)
![image](https://github.com/user-attachments/assets/ebc54bb8-d443-443c-86a6-63c21934ffa5)
![image](https://github.com/user-attachments/assets/dae85189-6623-4343-924d-2b8bfc0f1648)





