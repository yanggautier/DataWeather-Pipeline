import os
import time
from datetime import datetime
import pymongo
import logging
from dotenv import load_dotenv
from pathlib import Path
from .scripts.etl_to_mongodb import *


def measure_query_performance(collection, query, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.time()
        result = collection.find(query)
        end = time.time()
        times.append(end - start)

    return {
       'avg_time': sum(times) / len(times),
       'min_time': min(times),
       'max_time': max(times),
       'samples': times
   }


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Lire le fichier d'environnement pour AWS
    dotenv_path = Path('.env.awsecs')
    load_dotenv(dotenv_path=dotenv_path)

    MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
    MONGO_DB_PORT = os.getenv('MONGO_DB_PORT')
    MONGO_URI = f"{MONGO_DB_HOST}:{MONGO_DB_PORT}"

    client = pymongo.MongoClient(MONGO_URI)
    db = client.weathers

    weather_data = extract("data/output/final.json")
    load(weather_data, MONGO_URI)

    # Connexion
    client = pymongo.MongoClient(MONGO_URI)
    db = client.weathers
    collection = db.hourly

    print(collection.find_one({}))

    # Exemple de requête
    query = {
    'dh_utc': {'$gte': datetime(2024, 10, 6), '$lt': datetime(2024, 10, 7)},
    'id_station': 'ILAMAD25'
    }
    # Mesure
    results = measure_query_performance(collection, query)
    logger.info(f"Temps moyen: {results['avg_time']:.5f}s")
    logger.info(f"Temps min: {results['min_time']:.5f}s")
    logger.info(f"Temps max: {results['max_time']:.5f}s")
