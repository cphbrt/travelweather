################# Hello, fellow coder! Read the comments! ######################

# When we are testing the production functions locally, run this script via the
# command line like so:
# python functions.py

import json
import googlemaps
import darksky
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
    if request.method != 'POST':
        ret = {"issue": "not POST"}
        return (json.dumps(ret), 200, headers)
    if not request.is_json:
        ret = {"issue": "not JSON"}
        return (json.dumps(ret), 200, headers)
    incoming_dict = request.get_json()
    if "env" in incoming_dict:
        if incoming_dict['env'] == "dev":
            outgoing_dict = dev_outgoing_dict()
            return (json.dumps(outgoing_dict), 200, headers)
        elif incoming_dict['env'] == "prod":
            outgoing_dict = prod_outgoing_dict(incoming_dict)
            return (json.dumps(outgoing_dict), 200, headers)
        else:
            outgoing_dict = {"env": "misdeclared"}
            return (json.dumps(outgoing_dict), 200, headers)
    else:
        outgoing_dict = {"env": "undeclared"}
        return (json.dumps(outgoing_dict), 200, headers)

# This is the example response that we send back to index.html in dev mode.
# No real queries occur.
def dev_outgoing_dict():
    # This dictionary is an example of what functions.py should be sending to
    # index.html.
    outgoing_dict = {
        "hourly": [
            {
                "icon": "clear-night",
                "temp": 37.71,
                "time": "4:09 PM",
                "timezone": "America\/Chicago",
                "city": "Murfreesboro",
                "state": "TN"
            },
            {
                "icon": "clear-night",
                "temp": 36.65,
                "time": "4:09 PM",
                "timezone": "America\/Chicago",
                "city": "Thompson's Station",
                "state": "TN"
            },
            {
                "icon": "clear-night",
                "temp": 39.54,
                "time": "4:09 PM",
                "timezone": "America\/Chicago",
                "city": "McEwen",
                "state": "TN"
            },
            {
                "icon": "clear-night",
                "temp": 38.1,
                "time": "4:09 PM",
                "timezone": "America\/Chicago",
                "city": "Jackson",
                "state": "TN"
            },
            {
                "icon": "clear-night",
                "temp": 39.43,
                "time": "4:09 PM",
                "timezone": "America\/Chicago",
                "city": "Memphis",
                "state": "TN"
            }
        ]
    }
    return outgoing_dict

# This generates the actual real-world, API-querying response to its input.
# Executing this function counts towards our API request quotas.
def prod_outgoing_dict(incoming_dict):
    ## MAPS STUFF
    mapApiKey = os.getenv('MAP_API_KEY')
    gmaps = googlemaps.Client(key=mapApiKey)
    
    isLatLong = True
    for char in incoming_dict["start_location"]:
        if char.isalpha():
            isLatLong = False
    if not isLatLong:
        start_loc = gmaps.geocode(incoming_dict["start_location"])
    
    ## get lat/long
    if isLatLong:
        arrayLatLong = incoming_dict["start_location"].split(",") # looks like [ "3.4,5.6"]
        start_lat = arrayLatLong[0]
        start_long = arrayLatLong[1]
    else:
        start_lat =  start_loc[0]['geometry']['location']['lat']
        start_long = start_loc[0]['geometry']['location']['lng']

    # get directions 
    if isLatLong:
        start_location_strAddress = gmaps.reverse_geocode((start_lat, start_long))[0]["formatted_address"]
    else:
        start_location_strAddress = incoming_dict["start_location"]

    directions_response = gmaps.directions(
        start_location_strAddress,
        incoming_dict["end_location"], 
        mode=incoming_dict["method"], 
        departure_time=datetime.now()
    )

    # get all the points along the first route returned
    points = polyline.decode(directions_response[0]["overview_polyline"]["points"])

    durationSeconds = directions_response[0]["legs"][0]["duration"]["value"] # in units of seconds
    durationHours = int(round(durationSeconds/60/60)) # in units of hours
    if len(points) < durationHours:
        numIncrements = len(points)
    else:
        numIncrements = durationHours

    iterator = int(len(points) / numIncrements)

    incrementLatLongs = []
    incrementLatLongs.append({"lat": start_lat, "long": start_long})
    incrementDirections = []
    incrementDirections.append(directions_response)
    incrementArrivalTime = []
    incrementArrivalTime.append(0)
    finalvalue = 0
    for x in range(iterator, len(points), iterator):
        point_lat, point_long = points[x]
        incrementLatLongs.append({"lat": point_lat, "long": point_long})
        point_directions_response = gmaps.directions(
            start_location_strAddress,
            "{},{}".format(point_lat, point_long),
            mode=incoming_dict["method"],
            departure_time=datetime.now()
        )
        incrementDirections.append(point_directions_response)
        point_arrival_sec = point_directions_response[0]["legs"][0]["duration"]["value"]
        point_arrival_hour = int(round(point_arrival_sec/60/60))
        incrementArrivalTime.append(point_arrival_hour)
        finalvalue = x
    if finalvalue != len(points)-1:
        point_lat, point_long = points[-1]
        incrementLatLongs.append({"lat": point_lat, "long": point_long})
        point_directions_response = gmaps.directions(
            start_location_strAddress,
            "{},{}".format(point_lat, point_long),
            mode=incoming_dict["method"],
            departure_time=datetime.now()
        )
        incrementDirections.append(point_directions_response)
        point_arrival_sec = point_directions_response[0]["legs"][0]["duration"]["value"]
        point_arrival_hour = int(round(point_arrival_sec/60/60))
        incrementArrivalTime.append(point_arrival_hour)

    # DARK SKY (Weather)
    skyApiKey = os.getenv('SKY_API_KEY')

    incrementForecasts = []
    for x in incrementLatLongs:
        forecast = darksky.forecast(skyApiKey, x["lat"], x["long"])
        incrementForecasts.append(forecast)

    outgoing_dict = {
        "hourly": []
    }
    
    for x in range(0, len(incrementLatLongs)):
        thisForecast = incrementForecasts[x]
        thisTime = incrementArrivalTime[x]
        if x == 0:
            fullAddressStr = incrementDirections[x][0]["legs"][-1]["start_address"]
        else:
            fullAddressStr = incrementDirections[x][0]["legs"][-1]["end_address"]
        addressStrByComma = fullAddressStr.split(",")
        state = addressStrByComma[-2].strip().split(" ")[0]
        city = addressStrByComma[-3].strip()
        outgoing_dict["hourly"].append({
            "icon": thisForecast.hourly[thisTime].icon,
            "temp": thisForecast.hourly[thisTime].temperature,
            "time": datetime.fromtimestamp(thisForecast.hourly[thisTime].time).strftime("%-I:%M %p"),
            "timezone": thisForecast.timezone,
            "city": city,
            "state": state
        })

    return outgoing_dict

# This has a fake simulation the input we expect to get from index.html and it
# actually executes the production API requests on that fake input.
# Executing this function counts towards our API request quotas.
def test_prod_outgoing_dict():
    # This dictionary is an example of what index.html should be sending to
    # functions.py.
    # fake_incoming_dict = {
    #     "env": "prod",
    #     "start_location": "Murfreesboro, TN",
    #     "end_location": "Memphis, TN",
    #     "method": "driving"
    # }
    fake_incoming_dict = {
        "env": "prod",
        "start_location": "35.8465948,-86.36529569999999",
        "end_location": "Memphis, TN",
        "method": "driving"
    }
    # fake_incoming_dict = {
    #     "env": "prod",
    #     "start_location": "35.8465948,-86.36529569999999",
    #     "end_location": "Nashville, TN",
    #     "method": "driving"
    # }
    outgoing_dict = prod_outgoing_dict(fake_incoming_dict)
    print(json.dumps(outgoing_dict))

# Don't touch this. It helps testing locally work easily.
if __name__ == '__main__':
    test_prod_outgoing_dict()