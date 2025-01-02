import json
from datetime import datetime
import pymongo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract(file_path):
    """
    Fonction qui permet de lire la des données en json
    """
    with open(file_path) as json_data:
        try:
            weather_data = json.load(json_data)  
            logger.info("JSON chargé avec succès")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}")
            return None
    return weather_data


def load(weather_data, mongo_uri):
    """
    Fonction pour écrire les données du fichier JSON dans la base de données MongoDB
    """
    try:
        client = pymongo.MongoClient(mongo_uri)
        # Sélection ou création de base de données
        db = client.weathers

        # Importation de données dans la collection metadata 
        metadata = db.metadata
        metadata_existed_data = db.metadata.find({})
        if not len(list(metadata_existed_data)) > 0:
            metadata_data = weather_data["metadata"]
            metadata.insert_one(metadata_data)
            logger.info(f"Injection dans la collection metadata avec succès")
        else:
            logger.info(f"Données existent déjà dans la collection metadata")

        # Importation de données dans la collection stations 
        stations = db.stations
        stations_existed_data = db.stations.find({})
        if not len(list(stations_existed_data)) > 0:
            stations_data = weather_data["stations"]
            stations.insert_many(stations_data)
            logger.info(f"Injection dans la collection stations avec succès")
        else:
            logger.info(f"Données existent déjà dans la collection stations")

        # Importation de données dans la collection hourly 
        hourly = db.hourly
        hourly_existed_data = db.hourly.find({})
        if not len(list(hourly_existed_data)) > 0:
            hourly_data = weather_data["hourly"]      
            hourly.insert_many(hourly_data)
            logger.info(f"Injection dans la collection hourly avec succès")
        else:
            logger.info(f"Données existent déjà dans la collection hourly")

    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier JSON : {e}")
