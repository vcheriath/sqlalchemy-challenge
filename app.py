# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as datetime
from datetime import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
    # to a dictionary using date as the key and prcp as the value.
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = (dt.strptime(latest_date,"%Y-%m-%d") - datetime.timedelta(days=365)).date()
    
    measurement_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    
    all_measurements = []
    for date, prcp in measurement_data:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_measurements.append(measurement_dict)
    
    session.close()
    
    # Return the JSON representation of your dictionary.
    return jsonify(all_measurements)
    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Return a JSON list of stations from the dataset.
    station_list = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    all_stations = []
    for id, station, name, latitude, longitude, elevation in station_list:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
    session.close()
    return jsonify(all_stations)
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        all()
    most_active = active_stations[0][0]
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = (dt.strptime(latest_date,"%Y-%m-%d") - datetime.timedelta(days=365)).date()
    
    temp_list = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= query_date).\
        all()

    # Return a JSON list of temperature observations for the previous year.
    all_temps = []
    for date, tobs in temp_list:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = tobs
        all_temps.append(temp_dict)
    session.close()
    return jsonify(all_temps)
    
@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the maximum temperature for a specified start or start-end range.
    
    
    # For a specified start, calculate TMIN, TAVG, and TMAX for 
    # all the dates greater than or equal to the start date.
    try:
        start_date = dt.strptime(start,"%Y-%m-%d")
        
        TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
        
        session.close()
        return(
            f"Start Date: {start}<br/>"
            f"minimum temperature: {TMIN[0][0]}<br/>"
            f"maximum temperature: {TMAX[0][0]}<br/>"
            f"average temperature: {TAVG[0][0]}<br/>"    
        )
    except:
        session.close()
        return "Please enter a start date in the format <Y-m-d>"


@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the maximum temperature for a specified start or start-end range.
    
    # For a specified start date and end date, calculate TMIN, TAVG, 
    # and TMAX for the dates from the start date to the end date, inclusive.
    
    try:
        start_date = dt.strptime(start,"%Y-%m-%d")
        end_date = dt.strptime(end,"%Y-%m-%d")
        
        TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        
        session.close()
        return(
            f"Start Date: {start}<br/>"
            f"End Date: {end}<br/>"
            f"minimum temperature: {TMIN[0][0]}<br/>"
            f"maximum temperature: {TMAX[0][0]}<br/>"
            f"average temperature: {TAVG[0][0]}<br/>"    
        )
    except:
        session.close()
        return "Please enter a start date and end date in the format <Y-m-d>/<Y-m-d>"

if __name__ == '__main__':
    app.run(debug=True)