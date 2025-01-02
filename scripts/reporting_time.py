import os
import time
import pymongo
from datetime import datetime
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")


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

# Connexion
client = pymongo.MongoClient(MONGO_URI)
db = client.weathers
collection = db.hourly

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