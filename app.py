# Importing dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
# Initializing a variable with the created engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Initializing a variable with the last date of precipitation values held in
# Measurement
last_date = (session.query(Measurement.date).group_by(Measurement.date)
            .order_by(Measurement.date.desc()).first()[0])
# Formating the value held in last_date so that it is compatible with dt.date()
year = int(last_date[:4])
month = int(last_date[5:7])
date = int(last_date[8:10])
# Calculate the date 1 year ago from the last data point in the database
year_ago_date = dt.date(year, month, date) - dt.timedelta(days=365)
# Initializing a variable with a list of the distinct dates in the specified
# 1-year time period
list_of_dates_in_a_year = session.query(Measurement.date).distinct().\
                   filter(Measurement.date>=year_ago_date).\
                   filter(Measurement.date<=last_date).all()
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
# Home page.
@app.route("/api/v1.0/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp
    as the value."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Initializing an empty dict to hold the precipitation data for each date
    # in list_of_dates_in_a_year
    prcp_dict = {}
    # Initializing an index value for use in the following for-loop
    ind = 0
    # Using a for-loop to retrieve the precipitation data for each date in
    # list_of_dates_in_a_year and save it prcp_dict
    for entry in list_of_dates_in_a_year:
        date = list_of_dates_in_a_year[ind][0]
        prcp_on_date = session.query(Measurement.prcp).\
                       filter(Measurement.date == date).all()
        ind+=1
        prcp_dict.update({date: prcp_on_date})
    # Returning the jsonified version of prcp_dict
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Initialize a variable with the ID of each station
    stations = session.query(Measurement.station).distinct().all()
    # Initializing an empty list to hold the cleaned station ID's
    cleaned_stations = []
    #
    for entry in stations:
        station = entry[0]
        cleaned_stations.append(station)
    # Returning the jsonified version of the cleaned station ID's
    return jsonify(cleaned_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the
    last data point and then return a JSON list of Temperature Observations
    (tobs) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Initializing an empty dict to hold the precipitation data for each date
    # in list_of_dates_in_a_year
    tobs_dict = {}
    # Initializing an index value for use in the following for-loop
    ind = 0
    # Using a for-loop to retrieve the temperature data for each date in
    # list_of_dates_in_a_year and save it tobs_dict
    for entry in list_of_dates_in_a_year:
        date = list_of_dates_in_a_year[ind][0]
        tobs_on_date = session.query(Measurement.tobs).\
                       filter(Measurement.date == date).all()
        ind+=1
        tobs_dict.update({date: tobs_on_date})
    # Returning the jsonified version of tobs_dict
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates
    greater than and equal to the start date."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Initializing a variable with the query results
    results = session.query(func.min(Measurement.tobs),
              func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    # Returning the jsonified version of the query results
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """When given the start and the end date, calculate the TMIN, TAVG, and
    TMAX for dates between the start and end date inclusive."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Initializing a variable with the query results
    results = session.query(func.min(Measurement.tobs),
              func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()
    # Returning the jsonified version of the query results
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
