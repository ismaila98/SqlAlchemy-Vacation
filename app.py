import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*write a date*<br/>"
        f"/api/v1.0/*write a start date*/*write an end date*<br/>"
        f"Note: Date formate is yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
        session = Session(engine)
    # Calculate the date one year from the last date in data set.
        year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
        year_prcp = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date <= '2017-08-23').\
            filter(Measurement.date >= year_from_recent).all()

        prcp_dict = dict(year_prcp)
        return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station = session.query(Station.station).all() 
    return jsonify(list(np.ravel(station)))


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    most_active = session.query(Measurement.tobs).\
                        filter(Measurement.station == "USC00519281").\
                        filter(Measurement.date <= '2017-08-23').\
                        filter(Measurement.date >= '2016-08-23').all()
    return jsonify(list(np.ravel(most_active)))


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startDate(start, end = None):
    if end == None:
        end = '2017-08-23'
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.  
    min_max = session.query(func.min(Measurement.tobs), 
                                func.max(Measurement.tobs),
                                func.avg(Measurement.tobs)).\
                                filter(Measurement.date <= end).\
                                filter(Measurement.date >= start).all()
    return jsonify(list(np.ravel(min_max)))
