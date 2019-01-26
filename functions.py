# -*- coding: utf-8 -*-

################# Hello, fellow coder! Read the comments! ######################

# When we are testing the production functions locally, run this script via the
# command line like so:
# python functions.py

import json

# Only Bear can edit this one! Very delicate!
def handle_request(request):
    incoming_dict = request.get_json()
    if "env" not in incoming_dict:
        outgoing_dict = {"env":"undeclared"}
    elif incoming_dict['env'] == "dev":
        outgoing_dict = dev_outgoing_dict()
    elif incoming_dict['env'] == "prod":
        outgoing_dict = prod_outgoing_dict()
    else:
        outgoing_dict = {"env":"misdeclared"}
    return (json.dumps(outgoing_dict), 200, {
        'Access-Control-Allow-Origin':'*',
        'Content-Type':'application/json'
    })

# This is the example response that we send back to index.html in dev mode.
# No real queries occur.
def dev_outgoing_dict():
    # This dictionary is an example of what functions.py should be sending to
    # index.html.
    return {
        "env":"dev",
        "hourly": [
            {
                "lat": "38.8977",
                "long": "77.0365",
                "temp": "50°F"
            },
            {
                "lat": "35.8461",
                "long": "86.3655",
                "temp": "65°F"
            },
            {
                "lat": "37.4220",
                "long": "122.0841",
                "temp": "80°F"
            }
        ]
    }

# This generates the actual real-world, API-querying response to its input.
# Executing this function counts towards our API request quotas.
def prod_outgoing_dict(incoming_dict):
    # TODO: Query maps API
    # TODO: Query weather API
    # TODO: Do calculations...
    # TODO: Update outgoing_dict accordingly!
    outgoing_dict = {
        "env":"prod",
        "content":"real deal"
    }
    return outgoing_dict

# This has a fake simulation the input we expect to get from index.html and it
# actually executes the production API requests on that fake input.
# Executing this function counts towards our API request quotas.
def test_prod_outgoing_dict():
    # This dictionary is an example of what index.html should be sending to
    # functions.py.
    fake_incoming_dict = {
        "env":"prod",
        "start_location": {
            "lat": "38.8977",
            "long": "77.0365"
        },
        "end_location": {
            "lat": "37.4220",
            "long": "122.0841"
        }
    }
    outgoing_dict = prod_outgoing_dict(fake_incoming_dict)
    print(json.dumps(outgoing_dict))

# Don't touch this. It helps testing locally work easily.
if __name__ == '__main__':
    test_prod_outgoing_dict()
