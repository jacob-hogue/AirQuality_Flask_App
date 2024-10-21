import os
import json
import psycopg2
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy import func
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
app = Flask('app.py')
# Update app config with environment variables
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI=f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

# City mapping based on sensor_id
sensor_city_map = {
    1639: 'Fresno',
    24365: 'Hanford',
    24551: 'Madera',
    1328938: 'Bakersfield',
    1349599: 'Fresno',
    5077547: 'Bakersfield',
    5077593: 'Fresno',
    10280894: 'Visalia'
}

###------------------------------------LEFT OFF EDITING HERE-----------------------------------------------------###
class Cities(db.Model):
    __tablename__ = 'Polluted_CA_Cities'
    id = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('POLYGON'))
    name = db.Column(db.String, nullable=False)
    def __repr__(self):
        return f'ID: {self.id}, NAME: {self.name}'

class PointSensor(db.Model):
    __tablename__ = 'sensor_data'
    sensor_id = db.Column(db.Integer, primary_key=True)
    latest_value = db.Column(db.Float, nullable=False)
    summary_avg = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    

    def __repr__(self):
        return f'Lat: {self.lat}, Lon: {self.lon}, Id: {self.sensor_id}, Latest Value: {self.latest_value} pm25 µg/m³, Average Value: {self.summary_avg} pm25 µg/m³'

# Route to display data (Points) with all city Bounds
@app.route('/show_points', methods=['GET'])
def show_points():
    # Query to get coordinates from the database
    points = PointSensor.query.with_entities(PointSensor.lat, PointSensor.lon, PointSensor.sensor_id, PointSensor.latest_value,PointSensor.summary_avg).all()
    # Convert Row objects to a list of dictionaries or tuples
    points_list = [{'lat': point.lat, 'lon': point.lon, 'sensor_id': point.sensor_id, 'latest_value': point.latest_value, 'summary_avg': point.summary_avg} for point in points]
    print(points[0])
    print(type(points[0]))

    polygons = db.session.query(func.ST_AsGeoJSON(Cities.geom)).all()
    # Convert list of Row objects to a list of GeoJSON strings
    polygon_geojson = [polygon[0] for polygon in polygons]



    return render_template('app.html', polygons=polygon_geojson, points=points_list)

# Route to display a specific sensor with just that city Bound
@app.route('/sensor/<int:sensor_id>', methods=['GET'])
def get_sensor_by_id(sensor_id):
    # Query to get a specific sensor point from the database
    point = PointSensor.query.with_entities(PointSensor.lat, PointSensor.lon, PointSensor.sensor_id, PointSensor.latest_value, PointSensor.summary_avg).filter(PointSensor.sensor_id == sensor_id).first()
    
    if point:
        # Get the corresponding city name from the mapping
        city_name = sensor_city_map.get(sensor_id)

        if city_name:
            # Query to get the city polygon based on the city name
            city_polygon = db.session.query(func.ST_AsGeoJSON(Cities.geom)).filter(Cities.name == city_name).first()

            if city_polygon:
                # Convert the polygon to GeoJSON format
                city_polygon_geojson = city_polygon[0]
            else:
                city_polygon_geojson = None  # City not found
        else:
            city_polygon_geojson = None  # Sensor ID not mapped to a city

        # Convert the point to a dictionary
        point_data = {
            'lat': point.lat,
            'lon': point.lon,
            'sensor_id': point.sensor_id,
            'latest_value': point.latest_value,
            'summary_avg': point.summary_avg
        }
        
        return render_template('app.html', polygons=[city_polygon_geojson] if city_polygon_geojson else [], points=[point_data])  # Pass the single point as a list
    else:
        return f'Sensor ID {sensor_id} not found.', 404

   



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)