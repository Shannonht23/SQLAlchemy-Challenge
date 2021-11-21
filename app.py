import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()

    session.close()

    all_data = []
    for date, prcp in results:
         measure_dict = {}
         measure_dict[date] = prcp
         all_data.append(measure_dict)
    return jsonify(all_data)

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    """Return a list of all stations"""
    sel =[Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation,]
    results = session.query(*sel).all()
    session.close() #station	name	latitude	longitude	elevation

    all_data = []
    for station, name, latitude, longitude, elevation in results:
         station_dict = {}
         station_dict['station'] = station
         station_dict['name'] = name
         station_dict['latitude'] = latitude
         station_dict['longitude'] = longitude
         station_dict['elevation'] = elevation
         all_data.append(station_dict)
    
    return jsonify(all_data)

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    sel = [Measurement.station,
       func.count(Measurement.station)
      ]

    active_stations = session.query(*sel).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    active_stat_id = active_stations[0][0]
    max_date = session.query(func.max(Measurement.date)).filter(Measurement.station == active_stat_id).first()[0]

    # convert string to date object
    max_date = dt.datetime.strptime(max_date, '%Y-%m-%d').date()

    # Calculate the date one year from the last date in data set.
    year_ago = max_date - dt.timedelta(days=365)

    sel = [
       Measurement.date, 
       Measurement.tobs
     ]
    results = session.query(*sel).filter(Measurement.station == active_stat_id,Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()

    session.close() 

    all_data = []
    for date, tobs in results:
         tobs_dict = {}
         tobs_dict[date] = tobs
         all_data.append(tobs_dict)
    
    return jsonify(all_data)

@app.route("/api/v1.0/<start>")
def stats_start(start):
   
    session = Session(engine)

    sel = [
       func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)
      ]

    results = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    
    if results:
        all_data = results[0]
        all_data_dict = {
            'TMIN' :all_data[0],
            'TMAX' :all_data[1],
            'TAVG' :all_data[2]
        }
        return jsonify(all_data_dict)
        

    return jsonify({})

@app.route("/api/v1.0/<start>/<end>")
def stats_range(start,end):
   
    session = Session(engine)

    sel = [
       func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)
      ]

    results = session.query(*sel).filter(Measurement.date >= start,Measurement.date <= end).all()

    session.close()
    if results:
        all_data = results[0]
        all_data_dict = {
            'TMIN' :all_data[0],
            'TMAX' :all_data[1],
            'TAVG' :all_data[2]
        }
        return jsonify(all_data_dict)

    
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
