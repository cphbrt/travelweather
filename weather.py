from darksky import forecast
from datetime import date, timedelta, datetime
import os
import googlemaps
import polyline

#### INCOMING JSON
incoming_dict = {
    "env": "prod",
    "start_location": "Nashville, TN",
    "end_location": "San Diego, CA"
    
}

#### GOOGLE MAPS 
mapApiKey = os.getenv('MAP_API_KEY')
gmaps = googlemaps.Client(key=mapApiKey)
start_loc = gmaps.geocode(incoming_dict["start_location"])
end_loc = gmaps.geocode(incoming_dict["end_location"])

#### get lat/long
start_lat =  start_loc[0]['geometry']['location']['lat']
start_long = start_loc[0]['geometry']['location']['lng']

end_lat =  end_loc[0]['geometry']['location']['lat']
end_long = end_loc[0]['geometry']['location']['lng']

# get directions 
directions_response = gmaps.directions(
    incoming_dict["start_location"], 
    incoming_dict["end_location"], 
    mode="driving", 
    departure_time=datetime.now()
)

# get all the points along the first route returned
points = polyline.decode(directions_response[0]["overview_polyline"]["points"])

# get the middle point
lat, lng = points[int(len(points) / 2)]

#### DARK SKY 
skyApiKey = os.getenv('SKY_API_KEY')

### coordiate pairs
start_coordinates = start_lat, start_long
mid_coordinates = lat, lng
end_coordinates = end_lat, end_long

# get mid directions 
middirections_response = gmaps.directions(
    incoming_dict["start_location"], 
    "{},{}".format(lat, lng), 
    mode="driving", 
    departure_time=datetime.now()
)

### get forcast
start_forecast = forecast(skyApiKey, *start_coordinates)
mid_forecast = forecast(skyApiKey, *mid_coordinates)
end_forecast = forecast(skyApiKey, *end_coordinates)

start_weather = start_forecast.hourly[0].summary
start_temp = start_forecast.currently.temperature

### !!!!!!!!!!!!!! get time from maps?
mid_arrival_sec = middirections_response[0]["legs"][0]["duration"]["value"]
mid_arrival = int(round(mid_arrival_sec/60/60))

mid_weather = mid_forecast.hourly[mid_arrival].summary
mid_temp = mid_forecast.hourly[mid_arrival].temperature

### !!!!!!!!!!!!!! get time from maps?
end_arrival_sec = directions_response[0]["legs"][0]["duration"]["value"]
end_arrival = int(round(end_arrival_sec/60/60))



end_weather = end_forecast.hourly[end_arrival].summary
end_temp = end_forecast.hourly[end_arrival].temperature

### !!!!!!!!!!!!!! build array with "locations" ?

outgoing_dict = {
        "hourly": [
            {   "location": "start",
                "weather": start_weather,
                "temp": start_temp,
            },
            {   "location": "mid",
                "weather": mid_weather,
                "temp": mid_temp,
            },
            {
                "location": "end",
                "weather": end_weather,
                "temp": end_temp
            }
        ]
    }

print (outgoing_dict)
