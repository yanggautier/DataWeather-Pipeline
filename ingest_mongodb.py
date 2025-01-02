from scripts.etl_to_mongodb import *
import os

DATA_PATH = os.getenv("DATA_PATH")
MONGO_URI = os.getenv("MONGO_URI")

# Charger les données
weather_data = extract(f"{DATA_PATH}/output/final.json")
load(weather_data, MONGO_URI)