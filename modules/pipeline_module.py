import pandas as pd
import numpy as np
import requests

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from haversine import haversine, Unit

import re
import string

import os
from dotenv import load_dotenv

import argparse
import folium
from IPython.display import display
import json

import webbrowser

# Function to get place(s) of interest

def madrid_places(url,args=None):
    if args.mode == None:
        return print("Please enter app mode in the command line using the flag --mode")
    else:
        # Extract the data from Ayuntamiento de Madrid API REST 
        response = requests.get(url)
        json = response.json()
        df = pd.json_normalize(json["@graph"])
        # Exclude places without latitudes and longitudes
        df = df[df["location.latitude"].notna()]
        df = df[df["location.longitude"].notna()]
        df = df.reset_index()
        # String operations for place names and addresses
        df.loc[:,"address.street-address"] = df.loc[:,"address.street-address"].apply(lambda a: \
                                                                (lambda s: ', '.join(s.rsplit(' ', 1)) \
                                                                if any(char.isdigit() for char in s) else s)(a.title()))
        df.loc[:,'title'] = df.loc[:,'title'].apply(lambda x: x.replace("&amp;", "&"))
        title_counts = df.title.value_counts()
        # Rename duplicate place names
        filtered_counts = title_counts.loc[title_counts > 1]
        filtered_counts = list(filtered_counts.index)
        df['title'] = [df['title'][i] + '-' + df['address.street-address'][i] \
                        if df['title'][i] in filtered_counts \
                        else df['title'][i] \
                        for i in range(len(df))]
        # Filter the dataframe in case the user gives a specific place of interest     
        if args.mode == "Navigate":
            places = pd.DataFrame()
            names = list(df["title"].values)
            location = input('Please type your place of interest: ')
            while len(places) == 0:
                options = process.extract(location, names, scorer=fuzz.ratio)
                if options[0][1] == 100:
                    option = options[0][0]
                    places = df[df['title'] == option]
                else:
                    options = [options[i][0] for i in range(len(options))]
                    print('There are several matching heritage buildings:\n\n' +
                        '\n'.join(options) +
                        '\n\nPlease input the name of the desired place (copy the exact name)' +
                        '\n\nIf none of these options match your search, please enter again using more specific terms.'+
                        '\n\nIf you want to end the search, please type "Stop".')
                    location = input()
                    places = df[df['title'] == location]
                    if location == 'Stop':
                        return print('Thank you for using the app!')
        elif args.mode == "Explore":
            places = df
        return places

# Function to get bicimad stations

def bicimad_stations(user, passw, client_id, passkey):
    # Connect to EMT MADRID MobilityLabs API Reference
    login_header = {'email': user, 'password': passw, "X-ClientId": client_id, "passKey": passkey}
    login_url = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'
    login_response = requests.get(login_url, headers = login_header)
    login_json = login_response.json()
    bicimad_header = {'accessToken': login_json['data'][0]['accessToken']}
    bicimad_url = 'https://openapi.emtmadrid.es/v1/transport/bicimad/stations/'
    bicimad_response = requests.get(bicimad_url, headers = bicimad_header)
    bicimad_json = bicimad_response.json()
    stations = pd.json_normalize(bicimad_json["data"])
    # Define the variable "Available bikes"
    stations["Available bikes"] = stations["dock_bikes"] - stations["reservations_count"]
    # Filter stations with available bikes - User input
    while True:
        try:
            av_bi = int(input("To consider all BiciMAD stations input 1. For only those with bikes available input 0: "))
            if 0 <= av_bi <= 1:
                break
            else:
                print("Error: Input must be 0 or 1.")
        except ValueError:
            print("Error: Please enter a valid integer.")
    if av_bi == 0:
        stations = stations[stations['Available bikes'] != 0]
    # Filter stations depending on the number of available bikes - User input
        while True:
            try:
                num = int(input("Please specify minimum number of bikes (between 1 and 43) desired in a BiciMAD station: "))
                if 1 <= num <= 43:
                    stations = stations[stations['Available bikes'] >= num]
                    break
                else:
                    print("Error: Number must be between 1 and 30.")
            except ValueError:
                print("Error: Please enter a valid integer.")
    # Transform coordinate values
    stations["latitudes"] = [i[1] for i in stations["geometry.coordinates"]]
    stations["longitudes"] = [i[0] for i in stations["geometry.coordinates"]]
    stations = stations[['name','address','latitudes','longitudes','Available bikes']].copy()
    # String operations to modify station name and address
    stations["address"] = [i.replace(",Comunidad de Madrid España","") for i in stations["address"]]
    stations["address"] = [i[:-1] if i[-1] == "," else i for i in stations["address"]]
    stations["address"] = [i.replace(",",", ").replace(" , ",", ").replace("  "," ") for i in stations["address"]]
    stations["address"] = [i.replace(" nº ",", ") for i in stations["address"]]
    stations['name'] = stations['name'].apply(lambda x: re.findall(r"(?<=- ).*", x)[0])
    return stations

# Function to get the nearest station(s)

def nearest_bicimad_station(df_places, df_bicimad):
    # Join places of interest dataframe with bicimad stations dataframe 
    nearest_bicimad = df_places.join(df_bicimad, how='cross')
    # Calculate distances between places of interest and bicimad stations
    nearest_bicimad["Distance"] = nearest_bicimad.apply(
        lambda x : haversine(
            (x["location.latitude"], x["location.longitude"]),
            (x["latitudes"], x["longitudes"]),
            unit=Unit.METERS),
        axis=1)
    # Filter nearest bicimad stations to each place of interest
    nearest_bicimad = [nearest_bicimad[nearest_bicimad['title'] == p].query('Distance == Distance.min()') \
                       for p in df_places['title']]
    nearest_bicimad = pd.concat(nearest_bicimad)
    nearest_bicimad = nearest_bicimad.reset_index(drop=True)
    # Keep relevant columns and add "Type of place" column
    nearest_bicimad = nearest_bicimad.filter(items=['title', 'address.street-address','location.latitude'\
                                                    ,'location.longitude', 'name', 'address','latitudes'\
                                                    ,'longitudes','Available bikes', 'Distance'])
    nearest_bicimad.insert(1, "Type of place", "Patrimonio edificado")
    # Change column names
    keys = nearest_bicimad.columns
    values = ["Place of interest", "Type of place", "Place address","P-Latitude","P-Longitude"\
              ,'BiciMAD station', 'Station location',"B-Latitude","B-Longitude",'Available bikes','Distance']
    new_col = {k:v for k,v in zip(keys,values)}
    nearest_bicimad = nearest_bicimad.rename(columns = new_col)
    return nearest_bicimad

# Function to get outcomes

def outcome_all_places(df):
    df = df.filter(items=["Place of interest", "Type of place", "Place address", 'BiciMAD station', 'Station location', 'Available bikes'])
    df.to_csv('./outputs/nearest_station.csv', index=False)
    return print("Your file is ready! Thank you for using the app")

def outcome_one_place(df,key):
    # Get the coordinates of the place of interest and the nearest BiciMAD station
    place = [str(df['P-Latitude'][0]),str(df['P-Longitude'][0])]
    bicimad = [str(df['B-Latitude'][0]),str(df['B-Longitude'][0])]
    # Define the Open Route Service API endpoint and parameters
    endpoint = 'https://api.openrouteservice.org/v2/directions/foot-walking'
    params = {'api_key': key,
              'start': place[1] + ',' + place[0],
              'end': bicimad[1] + ',' + bicimad[0]
              }
    # Call the Open Route Service API
    response = requests.get(endpoint, params=params)
    data = json.loads(response.content)
    # Extract the coordinates of the walking route
    route_coords = [[i[1],i[0]] for i in data['features'][0]['geometry']['coordinates']]
    # Extract the duration of the walking route
    duration = data['features'][0]['properties']['segments'][0]['duration']
    if round(duration/60, 0) == 0:
        time_tag = "The walking distance between the two points is less than a minute.'"
    elif round(duration/60, 0) == 1:
        time_tag = f'The walking distance between the two points is {int(round(duration/60, 0))} minute.'
    else:
        time_tag = f'The walking distance between the two points is {int(round(duration/60, 0))} minutes.'
    # Create a map object
    map_ = folium.Map(location=[40.416775, -3.703790], zoom_start=10)
    # Add markers to the map with different colors and labels
    folium.Marker(location=place, popup=df['Place of interest'][0], icon=folium.Icon(color='red')).add_to(map_)
    folium.Marker(location=bicimad, popup=df['BiciMAD station'][0], icon=folium.Icon(color='blue')).add_to(map_)
    # Add the walking route to the map
    folium.PolyLine(locations=route_coords, tooltip=time_tag, color='green', weight=5).add_to(map_)
    # Save the map as an HTML file and open it in a web browser
    map_.save('./outputs/map.html')
    webbrowser.open_new_tab('./outputs/map.html')
    return print("Your directions map is ready! Thank you for using the app")