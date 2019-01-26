################# Hello, fellow coder! Read the comments! ######################

# When we are testing the production functions locally, run this script via the
# command line like so:
# python functions.py

import json
import googlemaps
from darksky import forecast
from datetime import date, timedelta, datetime
import os
import polyline

# Only Bear can edit this one! Very delicate!
def handle_request(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Content-Type': 'application/json'
    }
    incoming_dict = request.get_json()
    if "env" not in incoming_dict:
        outgoing_dict = {"env": "undeclared"}
        return (json.dumps(outgoing_dict), 200, headers)
    elif incoming_dict['env'] == "dev":
        outgoing_dict = dev_outgoing_dict()
        return (json.dumps(outgoing_dict), 200, headers)
    elif incoming_dict['env'] == "prod":
        outgoing_dict = prod_outgoing_dict(incoming_dict)
        return (json.dumps(outgoing_dict), 200, headers)
    else:
        outgoing_dict = {"env": "misdeclared"}
        return (json.dumps(outgoing_dict), 200, headers)

# This is the example response that we send back to index.html in dev mode.
# No real queries occur.
def dev_outgoing_dict():
    # This dictionary is an example of what functions.py should be sending to
    # index.html.
    outgoing_dict = {
        "env": "dev",
        "hourly": [
            {
                "lat": "38.8977",
                "long": "77.0365",
                "temp": "50"
            },
            {
                "lat": "35.8461",
                "long": "86.3655",
                "temp": "65"
            },
            {
                "lat": "37.4220",
                "long": "122.0841",
                "temp": "80"
            }
        ]
    }
    return outgoing_dict

# This generates the actual real-world, API-querying response to its input.
# Executing this function counts towards our API request quotas.
def prod_outgoing_dict(incoming_dict):
    # TODONE: GOOGLE MAPS
    mapApiKey = os.getenv('MAP_API_KEY')
    gmaps = googlemaps.Client(key=mapApiKey)
    start_loc = gmaps.geocode(incoming_dict["start_location"])
    end_loc = gmaps.geocode(incoming_dict["end_location"])
    now = datetime.now()
    
    ## get lat/long
    start_lat =  start_loc[0]['geometry']['location']['lat']
    start_long = start_loc[0]['geometry']['location']['lng']

    end_lat =  end_loc[0]['geometry']['location']['lat']
    end_long = end_loc[0]['geometry']['location']['lng']

    # get directions 
    directions_response = gmaps.directions(
        incoming_dict["start_location"], 
        incoming_dict["end_location"], 
        mode=incoming_dict["method"], 
        departure_time=datetime.now()
    )

    # get all the points along the first route returned
    points = polyline.decode(directions_response[0]["overview_polyline"]["points"])

    # get the middle points
    mid_lat, mid_long = points[int(len(points) / 2)]
    qtr_lat, qtr_long = points[int(len(points) / 4)]
    thqtr_lat, thqtr_long = points[(int(len(points)/4)*3)]

    # get middle directions 

    qtrdirections_response = gmaps.directions(
        incoming_dict["start_location"], 
        "{},{}".format(qtr_lat, qtr_long), 
        mode=incoming_dict["method"],
        departure_time=datetime.now()
    )

    middirections_response = gmaps.directions(
        incoming_dict["start_location"], 
        "{},{}".format(mid_lat, mid_long), 
        mode=incoming_dict["method"],
        departure_time=datetime.now()
    )

    thqtrdirections_response = gmaps.directions(
        incoming_dict["start_location"], 
        "{},{}".format(thqtr_lat, thqtr_long), 
        mode=incoming_dict["method"],
        departure_time=datetime.now()
    )

    
    #calc arrival times
    qtr_arrival_sec = qtrdirections_response[0]["legs"][0]["duration"]["value"]
    qtr_arrival = int(round(qtr_arrival_sec/60/60))

    mid_arrival_sec = middirections_response[0]["legs"][0]["duration"]["value"]
    mid_arrival = int(round(mid_arrival_sec/60/60))

    thqtr_arrival_sec = thqtrdirections_response[0]["legs"][0]["duration"]["value"]
    thqtr_arrival = int(round(thqtr_arrival_sec/60/60))

    end_arrival_sec = directions_response[0]["legs"][0]["duration"]["value"]
    end_arrival = int(round(end_arrival_sec/60/60))

    # TODONE: DARK SKY 
    skyApiKey = os.getenv('SKY_API_KEY')

    # coordiate pairs
    start_coordinates = start_lat, start_long
    qtr_coordinates = qtr_lat, qtr_long
    mid_coordinates = mid_lat, mid_long
    thqtr_coordinates = thqtr_lat, thqtr_long
    end_coordinates = end_lat, end_long

    # get forcasts
    start_forecast = forecast(skyApiKey, *start_coordinates)
    qtr_forecast = forecast(skyApiKey, *qtr_coordinates)
    mid_forecast = forecast(skyApiKey, *mid_coordinates)
    thqtr_forecast = forecast(skyApiKey, *thqtr_coordinates)
    end_forecast = forecast(skyApiKey, *end_coordinates)

    start_weather = start_forecast.hourly[0].summary
    start_temp = start_forecast.currently.temperature

    qtr_weather = mid_forecast.hourly[qtr_arrival].summary
    qtr_temp = mid_forecast.hourly[qtr_arrival].temperature

    mid_weather = mid_forecast.hourly[mid_arrival].summary
    mid_temp = mid_forecast.hourly[mid_arrival].temperature

    thqtr_weather = mid_forecast.hourly[thqtr_arrival].summary
    thqtr_temp = mid_forecast.hourly[thqtr_arrival].temperature

    end_weather = end_forecast.hourly[end_arrival].summary
    end_temp = end_forecast.hourly[end_arrival].temperature


    # TODO: Do calculations...

    outgoing_dict = {
            "hourly": [
                {   "location": "start",
                    "weather": start_weather,
                    "temp": start_temp,
                },
                {   "location": "qtr",
                    "weather": qtr_weather,
                    "temp": qtr_temp,
                },
                {   "location": "mid",
                    "weather": mid_weather,
                    "temp": mid_temp,
                },
                {   "location": "thqtr",
                    "weather": thqtr_weather,
                    "temp": thqtr_temp,
                },
                {
                    "location": "end",
                    "weather": end_weather,
                    "temp": end_temp
                }
            ]
        }
        
    # TODONE: Update outgoing_dict accordingly!
    return outgoing_dict

# This has a fake simulation the input we expect to get from index.html and it
# actually executes the production API requests on that fake input.
# Executing this function counts towards our API request quotas.
def test_prod_outgoing_dict():
    # This dictionary is an example of what index.html should be sending to
    # functions.py.
    fake_incoming_dict = {
        "env": "prod",
        "start_location": "Murfreesboro, TN",
        "end_location": "Nashville, TN",
        "method":
            "driving"

    }
    outgoing_dict = prod_outgoing_dict(fake_incoming_dict)
    print(json.dumps(outgoing_dict))

# Don't touch this. It helps testing locally work easily.
if __name__ == '__main__':
    test_prod_outgoing_dict()