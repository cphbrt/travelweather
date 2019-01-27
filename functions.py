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
    
    isLatLong = True
    for char in incoming_dict["start_location"]:
        if char.isalpha():
            isLatLong = False
    if not isLatLong:
        start_loc = gmaps.geocode(incoming_dict["start_location"])
    end_loc = gmaps.geocode(incoming_dict["end_location"])
    now = datetime.now()
    
    ## get lat/long
    if isLatLong:
        arrayLatLong = incoming_dict["start_location"].split(",") # looks like [ "3.4,5.6"]
        start_lat = arrayLatLong[0]
        start_long = arrayLatLong[1]
    else:
        start_lat =  start_loc[0]['geometry']['location']['lat']
        start_long = start_loc[0]['geometry']['location']['lng']

    end_lat =  end_loc[0]['geometry']['location']['lat']
    end_long = end_loc[0]['geometry']['location']['lng']

    # get directions 
    if isLatLong:
        start_location_strAddress = gmaps.reverse_geocode((start_lat, start_long))["results"][0]["formatted_address"]

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
    for x in range(iterator, numIncrements, iterator):
        point_lat, point_long = points[x]
        incrementLatLongs.append({"lat": point_lat, "long": point_long})
        point_directions_response = gmaps.directions(
            start_location_strAddress,
            "{},{}".format(point_lat, point_long),
            mode=incoming_dict["method"],
            departure_time=datetime.now()
        )
        incrementDirections.append(point_directions_response)
        # NOTE: the last increment added to these arrays might not be the last point!!!!
        # 51 / 10 rounds to 10 so 10 * 5 = 50, not 51
        point_arrival_sec = point_directions_response[0]["legs"][0]["duration"]["value"]
        point_arrival_hour = int(round(point_arrival_sec/60/60))
        incrementArrivalTime.append(point_arrival_hour)

    # TODONE: DARK SKY 
    skyApiKey = os.getenv('SKY_API_KEY')

    incrementForecasts = []
    for x in incrementLatLongs:
        forecast = darksky.forecast(skyApiKey, x["lat"], x["long"])
        incrementForecasts.append(forecast)
        
    # # coordiate pairs
    # start_coordinates = start_lat, start_long
    # qtr_coordinates = qtr_lat, qtr_long
    # mid_coordinates = mid_lat, mid_long
    # thqtr_coordinates = thqtr_lat, thqtr_long
    # end_coordinates = end_lat, end_long
    # 
    # # get forcasts
    # start_forecast = forecast(skyApiKey, *start_coordinates)
    # qtr_forecast = forecast(skyApiKey, *qtr_coordinates)
    # mid_forecast = forecast(skyApiKey, *mid_coordinates)
    # thqtr_forecast = forecast(skyApiKey, *thqtr_coordinates)
    # end_forecast = forecast(skyApiKey, *end_coordinates)

    #time, timezoe, citystate, distance, weather, temp
    # start_weather = start_forecast.hourly[0].summary
    # start_temp = start_forecast.currently.temperature
    # 
    # qtr_weather = mid_forecast.hourly[qtr_arrival].summary
    # qtr_temp = mid_forecast.hourly[qtr_arrival].temperature
    # 
    # mid_weather = mid_forecast.hourly[mid_arrival].summary
    # mid_temp = mid_forecast.hourly[mid_arrival].temperature
    # 
    # thqtr_weather = mid_forecast.hourly[thqtr_arrival].summary
    # thqtr_temp = mid_forecast.hourly[thqtr_arrival].temperature
    # 
    # end_weather = end_forecast.hourly[end_arrival].summary
    # end_temp = end_forecast.hourly[end_arrival].temperature


    # TODO: Do calculations...
    outgoing_dict = {
        "hourly": []
    }
    
    for x in range(0, numIncrements):
        thisForecast = incrementForecasts[x]
        thisTime = incrementArrivalTime[x]
        fullAddressStr = incrementDirections[x]["routes"][0]["legs"][-1]["end_address"]
        addressStrByComma = fullAddressStr.split(",")
        state = addressStrByComma[-2].strip().split(" ")[0]
        city = addressStrByComma[-3].strip()
        outgoing_dict["hourly"].append({
            "icon": thisForecast.hourly[thisTime].icon,
            "temp": thisForecast.hourly[thisTime].temperature,
            "time": thisForecast.hourly[thisTime].time, ## NOTE: needs to be converted
            "timezone": thisForecast.timezone,
            "city": city,
            "state": state
            #"icon": thisForecast["hourly"]["data"][thisTime]["icon"],
            #"temp": thisForecast["hourly"]["data"][thisTime]["temperature"],
            #"time": thisForecast["hourly"]["data"][thisTime]["time"] ## NOTE: needs to be converted
        })
    
    # outgoing_dict = {
    #         "hourly": [
    #             {   "location": "start",
    #                 "weather": start_weather,
    #                 "temp": start_temp,
    #             },
    #             {   "location": "qtr",
    #                 "weather": qtr_weather,
    #                 "temp": qtr_temp,
    #             },
    #             {   "location": "mid",
    #                 "weather": mid_weather,
    #                 "temp": mid_temp,
    #             },
    #             {   "location": "thqtr",
    #                 "weather": thqtr_weather,
    #                 "temp": thqtr_temp,
    #             },
    #             {
    #                 "location": "end",
    #                 "weather": end_weather,
    #                 "temp": end_temp
    #             }
    #         ]
    #     }
    
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
        "method": "driving"
    }
    # fake_incoming_dict = {
    #     "env": "prod",
    #     "start_location": "35.8465948,-86.36529569999999",
    #     "end_location": "Nashville, TN",
    #     "method":
    #         "driving"
    # }
    outgoing_dict = prod_outgoing_dict(fake_incoming_dict)
    print(json.dumps(outgoing_dict))

# Don't touch this. It helps testing locally work easily.
if __name__ == '__main__':
    test_prod_outgoing_dict()