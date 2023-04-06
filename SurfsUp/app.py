# 1. import Flask
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/julia/Dropbox/PC/Documents/GitHub/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
Base.classes.keys()

inspector = inspect(engine)
inspector.get_table_names()

# Save reference to the table
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Calculate the date one year from the last date in data set for later calculations.
import datetime as dt

year_before = dt.date(2017, 8 ,23) - dt.timedelta(days=365)

# Define the index route and list all the available routes.
@app.route("/")
def home():
    print("Server received request for API...")
    return (f"Welcome to my API<br/><br/>"
            f"Available Routes:<br/><br/>"
            f"/api/v1.0/precipitation<br/>"
            f"A list of precipitation data for the last 12 months of records<br/><br/>"
            f"/api/v1.0/stations<br/>"
            f"A list of stations included in the data<br/><br/>"
            f"/api/v1.0/tobs<br/>"
            f"A list of temperature data for the most active station recorded<br/><br/>"
            f"/api/v1.0/'start date'<br/>"
            f"Minimum, average and maximum temperature from your chosen start date - input your date in the format YYYY-MM-DD<br/><br/>"
            f"/api/v1.0/'start date'/'end date'<br/>"
            f"Minimum, average and maximum temperature between your chosen start and end dates - input your dates in the format YYYY-MM-DD")

#################################################
# Precipitation
#################################################

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list of precipitation results over last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_before).group_by(Measurement.date).all()

    session.close()

    # Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.
    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

#################################################
# Stations
#################################################

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Measurement.station.distinct()).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#################################################
# Tobs
#################################################

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates for the most active station in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= year_before).group_by(Measurement.date).all()

    session.close()
    
    # Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


#################################################
# Start date
#################################################

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start_date>")
def tobsdate(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).all()
    
    session.close()

    tobs_date_list = []
    for date, tobs in results:
        tobs_date_list.append(tobs)

    min_tobs_date = round(np.min(tobs_date_list),2)
    avg_tobs_date = round(np.mean(tobs_date_list),2)
    max_tobs_date = round(np.max(tobs_date_list),2)

    return (f"From {start_date}</br>"
            f"Minimum temperature was: {str(min_tobs_date)}</br>"
            f"Average temperature was: {str(avg_tobs_date)}</br>"
            f"Maximum temperature was: {str(max_tobs_date)}</br>")

#################################################
# Start and End dates
#################################################

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def tobsrange(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    tobs_range_list = []
    for date, tobs in results:
        tobs_range_list.append(tobs)

    min_tobs_range = round(np.min(tobs_range_list),2)
    avg_tobs_range = round(np.mean(tobs_range_list),2)
    max_tobs_range = round(np.max(tobs_range_list),2)

    return (f"Between {start} and {end}</br>"
            f"Minimum temperature was: {str(min_tobs_range)}</br>"
            f"Average temperature was: {str(avg_tobs_range)}</br>"
            f"Maximum temperature was: {str(max_tobs_range)}</br>")

# 5. Add code at the end of the file that will allow you to run the server from the command line
if __name__ == "__main__":
    app.run(debug=True)