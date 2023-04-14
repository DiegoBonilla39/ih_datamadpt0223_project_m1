#imports

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

from modules import pipeline_module as pipe

#input_variables

load_dotenv('./.env')

user = os.environ.get("user")
passw = os.environ.get("passw")
client_id = os.environ.get("client_id")
passkey = os.environ.get("passkey")
api_key = os.environ.get("api_key")
url_places = "https://datos.madrid.es/egob/catalogo/208844-0-monumentos-edificios.json"

#argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mode',type=str,default=None,help="Activate 'Explore' or 'Navigate'")
args = parser.parse_args()

#pipeline
if __name__ == '__main__':
    df_places = pipe.madrid_places(url_places,args)
    if df_places is not None:
        df_bicimad = pipe.bicimad_stations(user, passw, client_id, passkey)
        df_nearest = pipe.nearest_bicimad_station(df_places, df_bicimad)
        if len(df_nearest) == 1:
            pipe.outcome_one_place(df_nearest, api_key)
        else:
            pipe.outcome_all_places(df_nearest)