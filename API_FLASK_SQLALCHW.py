import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

##########  Database Configuration ##########
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

########## Flask Setup ##########
app = Flask(__name__)

########## Flask Routes ##########

@app.route("/")
def home():
    return (
        f"Hawaii Climate Analysis API<br/>"
        f"Routes/Endpoints:<br/>"
        f"- /api/v1.0/precipitation<br/>"
        f"- /api/v1.0/stations<br/>"
        f"- /api/v1.0/tobs<br/>"
        f"- /api/v1.0/temp/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def api_precipitation():
    # Return the precipitation data for the last year
    
    # Calculate the date 1 year ago from last date in database
    last_year = '2016-08-23'

    # Query for the date and precipitation for the last year
    rain_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    # Convert to list of tuples (form SQL) to DataFrame
    precip_df = pd.DataFrame(rain_query)

    # Convert DataFrame to list of dictionaries (records)
    precip = precip_df.to_dict('records')
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def api_stations():
    # return list of stations available
    results = session.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def api_temp_monthly():
    # Calculate the date 1 year ago from last date in database
    last_year = '2016-08-23'

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def api_stats(start=None, end=None):
    # Return TMIN, TAVG, and TMAX

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
  
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)



########## Run the App ##########
if __name__ == '__main__':
  app.run()