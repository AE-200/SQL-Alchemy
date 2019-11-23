#%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, jsonify


import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

first_date=session.query(Measurement.date).order_by(Measurement.date).first()
latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

query=datetime.strptime(latest_date,"%Y-%m-%d")-dt.timedelta(days=365)
end_date=datetime.strptime(latest_date, "%Y-%m-%d")

# Design a query to retrieve the last 12 months of precipitation data and plot the results
# Perform a query to retrieve the data and precipitation scores

prcp_results=session.query(Measurement.date, Measurement.prcp).\
     filter(Measurement.date>=query).\
     group_by(Measurement.date).\
     order_by(Measurement.date).all()

active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
     group_by(Measurement.station).\
     order_by(func.count(Measurement.station).desc()).all()

temp_stats=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
               filter(Measurement.station ==active_stations[0][0]).all()

temp_results=session.query(Measurement.date, Measurement.tobs).\
     filter(Measurement.date>=query).\
     filter(Measurement.station==active_stations[0][0]).\
     order_by(Measurement.date).all()


# 2. Create an app
app = Flask(__name__)


# 3. Define static routes
@app.route("/")
def home():
    return f"Welcome to the climate API!<br/>
           Routes available are:<br/>
           /api/v1.0/precipitation<br/>
           /api/v1.0/stations<br/>
           /api/v1.0/tobs<br/>
           /api/v1.0/<start><br/>
           /api/v1.0/<start>/<end>"

    
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_dict=dict(prcp_results)
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    station_list=session.query(Station.station, Station.name).all()
    station_dict=dict(station_list)
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    temp_obs=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date>=query).\
        order_by(Measurement.date).all()
    temp_obs_dict=dict(temp_obs)
    return jsonify(temp_obs_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):

    t_obs=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    t_obs_dict={'Minimum Temperature':t_obs[0][0], 'Average Temperature':t_obs[0][1], 'Maximum Temperature':t_obs[0][2]}
       
    return jsonify(t_obs_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    t_obs_start_end=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    t_obs_dict_start_end={'Minimum Temperature':t_obs_start_end[0][0], 'Average Temperature':t_obs_start_end[0][1], 'Maximum Temperature':t_obs_start_end[0][2]}
       
    return jsonify(t_obs_dict_start_end)


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
