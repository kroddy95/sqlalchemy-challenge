from scipy import stats 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create an app, being sure to pass __name__
app = Flask(__name__)


# At index give list of routes
@app.route("/")
def home():
   return (
        f"Welcome to the Climate App API<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

# First Route
@app.route("/api/v1.0/precipitation")
def prcp():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    min_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date() - dt.timedelta(weeks=52)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= min_date).\
    order_by(Measurement.date.desc()).all()

    # Close session
    session.close()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        # prcp_dict["date"] = date
        # prcp_dict["prcp"] = prcp
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    # prcp_list = list(np.ravel(results))
    return jsonify(prcp_list)

# Second Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Get the list of stations and their count of measurements
    stations = session.query(Measurement.station).group_by(Measurement.station).\
                                order_by(Measurement.station.desc()).all()

    session.close()

    # Change to normal list
    output = list(np.ravel(stations))
    return jsonify(output)


# Third Route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

     # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    min_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date() - dt.timedelta(weeks=52)

    # Get the info for the most active station
    station_info = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= min_date).all()

    session.close()

    output = list(np.ravel(station_info))
    return jsonify(output)

# Start Date Route
@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date > start).all()

    session.close()

    output = [{"Min Temp" : results[0][0]}, {"Max Temp" : results[0][1]}, {"Avg Temp" : results[0][2]}]
    return jsonify(output)

# Start Date/End Date Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date > start).filter(Measurement.date < end).all()

    session.close()

    output = [{"Min Temp" : results[0][0]}, {"Max Temp" : results[0][1]}, {"Avg Temp" : results[0][2]}]
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)
