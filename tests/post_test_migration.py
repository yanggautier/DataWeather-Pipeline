import unittest
from pymongo import MongoClient
import json
import os

DATA_PATH = os.getenv("DATA_PATH")
MONGO_URI = os.getenv("MONGO_URI")

class PostDataIntegrityTest(unittest.TestCase):
    def setUp(self):

        with open(f"{DATA_PATH}/output/final.json", 'r') as fp:
            self.data = json.load(fp)
    
        self.client = MongoClient(MONGO_URI)

        # Connexion à la base de données MongoDB 
        self.db = self.client.weathers

    def tearDown(self):
        self.client.close()
    
    def test_data_counts(self):
        stations_count = self.db.stations.count_documents({})
        hourly_count = self.db.hourly.count_documents({})
        
        self.assertEqual(stations_count, len(self.data['stations']), 
                        "Nombre de stations différent après migration")
        self.assertEqual(hourly_count, len(self.data['hourly']), 
                        "Nombre de mesures horaires différent après migration")
    
    def test_data_integrity(self):
        # Test intégrité stations
        for station in self.data['stations']:
            db_station = self.db.stations.find_one({'id': station['id']})
            self.assertIsNotNone(db_station, f"Station {station['id']} non trouvée")
            self.assertEqual(station['name'], db_station['name'])
            self.assertEqual(station['latitude'], db_station['latitude'])
            
        # Test intégrité données horaires
        sample_hourly = self.data['hourly'][0]
        db_hourly = self.db.hourly.find_one({
            'id_station': sample_hourly['id_station'],
            'dh_utc': sample_hourly['dh_utc']
        })
        self.assertIsNotNone(db_hourly, "Données horaires non trouvées")
        self.assertEqual(float(sample_hourly['temperature']), float(db_hourly['temperature']))
        

if __name__ == '__main__':
    unittest.main()