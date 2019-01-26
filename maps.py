import json
import googlemaps
from datetime import datetime

incoming_dict = {
        "env": "prod",
        "start_location":
            "Murfreesboro, TN"
        ,
        "end_location": 
            "Nashville, TN"
    }

gmaps = googlemaps.Client(key='AIzaSyDV2o9Pb5PCFx4q841-NvmQvSrStDFBINw')
start_loc = gmaps.geocode(incoming_dict["start_location"])
end_loc = gmaps.geocode(incoming_dict["end_location"])
print(start_loc[0]["geometry"]["location"]["lat"], start_loc[0]["geometry"]["location"]["lng"])
print(end_loc[0]["geometry"]["location"]["lat"], end_loc[0]["geometry"]["location"]["lng"])

now = datetime.now()
directions_result = gmaps.directions(incoming_dict["start_location"],
                                     incoming_dict["end_location"],
                                     mode="bicycling",
                                     departure_time=now)
print(directions_result)
print(directions_result["Pj"]["warnings"])
