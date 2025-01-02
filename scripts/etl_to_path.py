import pandas as pd
import numpy as np
import json
from datetime import datetime
import re
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract(station_json_path, ichtegem_xlsx_path, madeleine_xlsx_path):
    """
    Fonction qui permet de lire la des données (fichiers json et xlsx), et
    """
    with open(station_json_path) as json_data:
        try:
            list_stations_data = json.load(json_data)  
            logger.info("JSON chargé avec succès")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}")
            return None
    try:
        # Lire le fichier excel de station ichtegem
        xlsx_ichtegem = pd.ExcelFile(ichtegem_xlsx_path)
        underground_df = pd.DataFrame({})
        days = xlsx_ichtegem.sheet_names

        for day in days:
            day_df = pd.read_excel(xlsx_ichtegem, day).iloc[1:, :]
            day_df["Date"] = f"2024-10-{day[:2]}"
            underground_df = pd.concat([underground_df, day_df], ignore_index=True)

        logger.info(f"Fichier Weather Underground Ichtegem.chargé avec {len(underground_df)} lignes")

        # Lire le fichier excel de station Madeleine
        xlsx_madeleine = pd.ExcelFile(madeleine_xlsx_path)
        madeleine_df = pd.DataFrame({})
        days = xlsx_madeleine.sheet_names

        for day in days:
            day_df = pd.read_excel(xlsx_madeleine, day).iloc[1:, :]
            day_df["Date"] = f"2024-10-{day[:2]}"
            madeleine_df = pd.concat([madeleine_df, day_df], ignore_index=True)
            
        logger.info(f"Fichier Weather Underground Madeleine chargé avec {len(madeleine_df)} lignes")


    except Exception as e:
        logger.error(f"Erreur de lecture Excel: {e}")
        return None
    
    return list_stations_data,  underground_df, madeleine_df


def transform(stations_data, df_ichtegem, df_madeleine):
    """
        Fonction qui permet de nettoyer les données en entrée et de fusionnerpl puis en sortie un fichier json à la sortie.
    """
    
    def clean_numeric(value):
        """Extraire des valeurs numériques à partir de chaîne de caractère"""
        if pd.isna(value):
            return None
        match = re.search(r'([-\d.]+)', str(value))
        return float(match.group(1)) if match else None

    def fahrenheit_to_celsius(f):
        """Conversion de Fahrenheit à Celsius"""
        if f is None:
            return None
        return round((f - 32) * 5/9, 1)

    def inhg_to_hpa(inhg):
        """Conversion de of mercury inche à hectopascal"""
        if inhg is None:
            return None
        return round(inhg * 33.8639, 1)

    def mph_to_kmh(mph):
        """Conversion de mile par heure par mètre par seconde"""
        if mph is None:
            return None
        return round(mph * 1.60934, 1)

    def in_to_mm(pouce):
            """Conversion de pouce à mm"""
            if pouce is None:
                return None
            return round(pouce * 25.4, 2)

    def extract_wind_direction(direction):
        """Conversion de direction cardinal à degrée"""

        direction_map = {
            'North': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'EAST': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'SOUTH': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'WEST': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        return direction_map.get(direction)


    def transform_weather_data(df, station_id):
        """Transformer DataFrame au format liste de dictionnaire"""
        
        df = df.copy()
        # Extraction de données numériques à partir des colonnes données
        columns = ['Temperature', 'Dew Point', 'Humidity', 'Speed', 'Gust', 'Pressure', 'Precip. Rate.', 'Precip. Accum.', 'UV', 'Solar']
        for column in columns:
            df[column] = df[column].apply(clean_numeric)
        try:
            # Transformation de données à l'aide des fonctions définies en haut
            df["id_station"] = station_id
            df["dh_utc"] = df["Date"] + " " + df["Time"].astype(str)
            df["temperature"]= df["Temperature"].astype(float).apply(fahrenheit_to_celsius)
            df["pression"]= df["Pressure"].astype(float).apply(inhg_to_hpa)
            df["humidite"] = df["Humidity"]
            df["point_de_rosee"] = df["Dew Point"].astype(float).apply(fahrenheit_to_celsius)
            df["vent_moyen"]= df["Speed"].astype(float).apply(mph_to_kmh)
            df["vent_rafales"]= df["Gust"].astype(float).apply(mph_to_kmh)
            df["vent_direction"] = df["Wind"].str.upper().map(extract_wind_direction)
            df["precip_rate"]= df["Precip. Rate."].astype(float).apply(in_to_mm)
            df["precip_accum"]= df["Precip. Accum."].astype(float).apply(in_to_mm)
            df.rename(columns={"Solar": "solar", "UV": "uv"}, inplace=True)
            df = df.replace(np.nan, None)
            df = df.replace("", None)
            # Sélectionner les colonnes transformées
            output_columns = ["id_station", "dh_utc", "temperature", "pression", "humidite", "point_de_rosee", "vent_moyen",
                         "vent_rafales", "vent_direction", "precip_rate", "precip_accum", "solar", "uv"]
        except Exception as e:
            logger.error(f"Erreur de transformation: {e}")
            return None
        
        # Sortie en dictionnaire
        return df[output_columns].to_dict('records')

    stations = stations_data["stations"]
    metadata = stations_data["metadata"]
    hourly = stations_data["hourly"]
    
    for station in stations:
        station["source"] = "InfoClimat"
        
    new_stations = stations + [{'id': 'IICHTE19',
                        'name': 'WeerstationBS',
                        'latitude': 51.092,
                        'longitude': 2.999,
                        'elevation': 15,
                        'source': 'Weather Underground',
                        'hardware': 'other',
                        'software': 'EasyWeatherV1.6.6'},
                        {'id': 'ILAMAD25',
                        'name': 'La Madeleine',
                        'latitude': 50.659,
                        'longitude': 3.07,
                         'elevation': 23,
                        'source': 'Weather Underground',
                        'hardware': 'other',
                        'software': 'EasyWeatherPro_V5.1.6'}]
    
    metadata["hardware"] = "type of hardware used"
    metadata["software"] = "software used"
    
    hourly["IICHTE19"] = transform_weather_data(df_ichtegem, "IICHTE19")
    hourly["ILAMAD25"] = transform_weather_data(df_madeleine, "ILAMAD25")
    
    # Récupérant les données de temps en une liste
    my_list = []
    for key, value in hourly.items():
        if key != "_params":
            my_list = my_list + value
        
    return {'stations': new_stations, 
            'metadata': metadata,
            'hourly': my_list}


def load(data, output_path):
    """
    Fonction pour écrire un fichier JSON correctement formaté.
    """
    try:
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Sérialiser les données en JSON
        with open(output_path, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, indent=4, ensure_ascii=False, default=str)
        logger.info(f"Fichier JSON écrit avec succès dans : {output_path}")
    except TypeError as e:
        logger.error(f"Erreur de sérialisation : {e}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier JSON : {e}")
