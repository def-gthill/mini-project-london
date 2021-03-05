"""
A little console program to plan bus and tube trips
in London
"""

import requests as re

import tfl_env as env

app_id = env.PRIMARY_KEY
app_key = env.SECONDARY_KEY


def main():
    response = None

    while True:
        if response is None:
            start = input("Enter the start location: ")
            end = input("Enter the end location: ")
            response = get_journey(start, end)

        if response.status_code == 200:
            break
        elif response.status_code == 300:
            response = disambiguate(start, end, response.json())
        else:
            print("Couldn't understand the locations; please try again.")
            response = None
    
    show_trip_plan(response.json())


def get_journey(start, end):
    return get_tfl(
        f"Journey/JourneyResults/{start}/to/{end}",
        mode="bus,tube",
        time=1500,
        timeIs="departing",
    )
            

def get_tfl(endpoint, **params):
    params["app_id"] = app_id
    params["app_key"] = app_key
    return re.get(
        f"https://api.tfl.gov.uk/{endpoint}",
        params
    )


def disambiguate(start, end, response_json):
    new_start = disambiguate_location(
        start, response_json['fromLocationDisambiguation']
    )
    new_end = disambiguate_location(
        end, response_json['toLocationDisambiguation']
    )
    return get_journey(new_start, new_end)


def disambiguate_location(location, disambiguation):
    if disambiguation['matchStatus'] == 'identified':
        return location
    options = disambiguation['disambiguationOptions']
    if len(options) == 1:
        return options[0]['parameterValue']
    else:
        print(f"\"{location}\" matches {len(options)} locations:")
        for i in range(min(len(options), 5)):
            option_name = options[i]['place']['commonName']
            print(f"{i + 1}: {option_name}")
        choice = input("Please enter the number (1-5) of the location you want: ")
        return options[int(choice) - 1]['parameterValue']


def find_with_value(ls, key, value):
    """
    In list of dictionaries ``ls``, find the first dictionary
    that maps ``key`` to ``value``
    """
    for d in ls:
        if key in d and d[key] == value:
            return d


def show_trip_plan(response_json):
    journey = response_json['journeys'][0]
    print(f"Total trip time: {journey['duration']} minutes")
    for leg in journey['legs']:
        print(f"{leg['instruction']['summary']} ({leg['duration']} minutes)")


if __name__ == "__main__":
    main()

