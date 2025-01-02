from pymongo import MongoClient
import os
import json
import pandas as pd
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    def __init__(self, uri: str):
        self.uri = uri

        self.client = MongoClient(uri)

        self.db = self.client.weathers

        self.stations_data = list(self.db.stations.find({}))
        self.hourly_data = list(self.db.hourly.find({}))

        self.stations_schema = {
            'id': str,
            'name': str,
            'latitude': float,
            'longitude': float,
            'elevation': int
        }
        
        self.hourly_schema = {
            'id_station': str,
            'dh_utc': str,
            'temperature': float,
            'pression': float,
            'humidite': float,
            'point_de_rosee': float,
            'vent_moyen': float,
            'vent_rafales': float,
            'vent_direction': float
        }

    def validate_type(self, value, expected_type):
        if value is None:
            return True
        try:
            if expected_type == float:
                float(value)
            elif expected_type == int:
                int(value)
            elif expected_type == str:
                str(value)
            return True
        except:
            return False

    def validate_stations(self, stations: List[Dict]) -> Dict:
        errors = []
        for station in stations:
            for field, expected_type in self.stations_schema.items():
                if field not in station:
                    errors.append(f"Missing field {field} in station {station.get('id', 'unknown')}")
                elif not self.validate_type(station[field], expected_type):
                    errors.append(f"Invalid type for {field} in station {station['id']}")
                    
        duplicates = pd.DataFrame(stations)['id'].duplicated().sum()
        
        return {
            'valid_records': len(stations) - len(errors),
            'error_rate': round(len(errors)/len(stations)),
            'invalid_records': len(errors),
            'duplicates': duplicates,
            'errors': errors
        }

    def validate_hourly(self, hourly: List[Dict]) -> Dict:
        errors = []
        for record in hourly:
            for field, expected_type in self.hourly_schema.items():
                if field not in record:
                    errors.append(f"Missing field {field} in record {record.get('id_station', 'unknown')}")
                elif not self.validate_type(record[field], expected_type):
                    errors.append(f"Invalid type for {field} in record {record['id_station']}")
                    
        df = pd.DataFrame(hourly)
        duplicates = df.duplicated(subset=['id_station', 'dh_utc']).sum()
        missing_values = df.isnull().sum().to_dict()
        
        return {
            'valid_records': len(hourly) - len(errors),
            'invalid_records': len(errors),
            'error_rate': round(len(errors)/len(hourly)),
            'duplicates': duplicates,
            'missing_values': missing_values,
            'errors': errors
        }

    def validation(self):
        
        # Validation 
        stations_validation = self.validate_stations(self.stations_data)
        hourly_validation = self.validate_hourly(self.hourly_data)
        
        logger.info(f"Stations: {stations_validation}")
        logger.info(f"Hourly: {hourly_validation}")
        
        return {
            'post_migration': {
                'stations_count': stations_validation,
                'hourly_count': hourly_validation
            }
        }

def main():

    MONGO_URI = os.getenv("MONGO_URI")  
    # Migration
    validator = DataValidator(MONGO_URI)
    results = validator.validation()
    
    logger.info(f"Results: {results}")

if __name__ == "__main__":
    main()