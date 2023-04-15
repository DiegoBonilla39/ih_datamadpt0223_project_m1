
# 🚲 BiciMAD Go-To
The go-to app for finding bike stations in Madrid
## 🖹 Description

Love exploring the city on two wheels? Let BiciMAD Go-To be your guide! 

BiciMAD Go-To is an app designed for bicycle enthusiasts who want to make the most of their urban adventures using the BiciMAD service.

This app is the perfect tool to find the nearest BiciMAD station to a place of interest, providing the following options:

- 🔎 **Explore Mode** - Provides users with a list of the nearest BiciMAD stations to a set of multiple places of interest.
- 🗺️ **Navigate Mode** - Guides users to the nearest BiciMAD station from a specific place of interest and provides a walking route to get there.

Get ready to pedal your way to new adventures with BiciMAD Go-To!


## 🤖 App Specifications

📚 App designed as the Module 1 Project for the Ironhack Data Analytics Bootcamp

⚠️ At the moment, BiciMAD Go-To only provides information on places categorized by the Community of Madrid as "**Heritage Building**"

🚧 Further updates **to be continued**.



## 📁 Folder Structure

```bash
└── project
    ├── .gitignore
    ├── README.md
    ├── main.py
    ├── outputs
    │   └── .gitkeep
    └── modules
        └── pipeline_module.py

```
    
## 💻 Technology Stack

**Data Analysis and Manipulation:**
- pandas
- numpy
- json
- haversine


**String operations:**
- fuzzywuzzy
- string
- re

**API and Environment Variables Requests:**
- requests
- dotenv

**Command-Line Interface:**
- argparse

**Visualization:**
- folium
- webbrowser


## 🔧 Requirements


Create an account in https://mobilitylabs.emtmadrid.es/
- Create a new app to extract data from BiciMAD and wait for its approval
- When approved, you have to save the following variables in a .env file with the following names:
    - user = 'your email'
    - passwo = 'your password'
    - client_id ='your client_id' 
    - passkey = 'your passkey'

Sign up on https://api.openrouteservice.org/ by creating an account:
- Create a token and save the api_key in a .env file with:
    - api_key='your api_key'


## 🚀 How To Run & What To Get

🔎 Explore Mode 

```bash
  python main.py --mode="Explore"
```
- Output ➡️ Table
    - Filename: all_nearest_station
    - Format: .csv
    - Location: Folder "outputs"

Place of interest | Type of place | Place address | BiciMAD station | Station location | Available bikes
--- | --- | --- | --- |--- |---
Almacenes Rodríguez | Patrimonio edificado | Calle Caballero De Gracia, 3 | Plaza de Pedro Zerolo | Plaza de Pedro Zerolo, 1 | 3 
... | ... | ... | ... | ... | ... 

------
\
🗺️ Navigate Mode

```bash
  python main.py --mode="Navigate"
```
- Output ➡️ Directions Map
    - Filename: map
    - Format: .html
    - Location: Opens in browser and saves in the "project" folder 
- Output ➡️ Table
    - Filename: one_nearest_station
    - Format: .csv
    - Location: Folder "outputs"


## 🔜 Roadmap

- Create a system to obtain missing coordinates using the addresses of the sites of interest.
- In the “Explore Mode”, give the user the option to choose how to get the final table (e.g. a specific route).
- Create a modality within the "Navigation Mode" that gives users 5 possible BiciMAD stations instead of one.

