# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all the available routes."""
    return (
        f"Welcome to the Precipitation Page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end/<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    measurement_df = pd.read_sql_query("SELECT date FROM measurement ORDER BY date DESC LIMIT 1", engine)
    
    recent_date = measurement_df["date"].iloc[0]

    prev_year = dt.datetime.strptime(recent_date, "%Y-%m-%d").date() - dt.timedelta(365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))

    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8 , 23) - dt.timedelta(days=365)
    stations = session.query(Measurement.station, func.count()).group_by(Measurement.station).\
    order_by(func.count().desc()).all()
    active_station = stations[0][0]

    results = session.query(Measurement.tobs).filter(Measurement.station == active_station).filter(Measurement.date >= prev_year).all()
    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None,end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]

    if not sel:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).filter(Measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))

        return jsonify(temps)
    start = dt.datetime.strptime(start , "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).filter(Measurement.date >=start).filter(Measurement.date <= end).all()

    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
if __name__ == "__main__":
    app.run(debug=True)