import os
import json
import pandas as pd
import numpy as np

# =================================================================
# Tratamento de dados de vendas
df_data = pd.read_csv("Dataset/nyc-rolling-sales.csv", index_col=0)

df_data = df_data.replace(' -  ', 0)
object_cols = ["LAND SQUARE FEET", "GROSS SQUARE FEET", "SALE PRICE"]
df_data[object_cols] = df_data[object_cols].astype(np.float)
df_data["SALE DATE"] = pd.to_datetime(df_data["SALE DATE"])

df_data = df_data[df_data["SALE PRICE"] != 0]
df_data = df_data[df_data["LAND SQUARE FEET"] != 0]
df_data = df_data[df_data["GROSS SQUARE FEET"] != 0]

# =================================================================
# Tratamento de dados LATITUDES e LONGITUDES
import requests

here_api = open("keys/here_api").read()
dict_address = json.load(open('dict_notes.json'))
error = []
c = 0
total = len(df_data["ADDRESS"].unique())

for address in df_data["ADDRESS"].unique():
    try:
        if address in dict_address.keys():
            continue
        URL = "https://geocode.search.hereapi.com/v1/geocode"
        location =  address + ", NYC"
        PARAMS = {'apikey':here_api,'q':location} 
        r = requests.get(url = URL, params = PARAMS) 
        data = r.json()

        lat = data['items'][0]['position']['lat']
        long = data['items'][0]['position']['lng']
        dict_address[address] = {"latitude": lat, "longitude": long}
        with open('dict_notes.json', 'w') as f:
            json.dump(dict_address, f)
        
    except Exception as e:
        print(e)
        error += [address]

    c += 1
    print(c, total)

# ===================================
# Tratamento final

dict_address = json.load(open('dict_notes.json'))

# LATITUDE AND LONGITUDE
dict_lat = {key: value["latitude"] for key, value in dict_address.items()}
dict_long = {key: value["longitude"] for key, value in dict_address.items()}

df_data["LATITUDE"] = df_data["ADDRESS"].map(dict_lat)
df_data["LONGITUDE"] = df_data["ADDRESS"].map(dict_long)
df_data.to_csv("Dataset/cleaned_data.csv")