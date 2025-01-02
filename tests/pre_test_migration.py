import unittest
import pandas as pd
import json
import os

DATA_PATH = os.getenv("DATA_PATH")


class PreDataIntegrityTest(unittest.TestCase):
    def setUp(self):
        # Chemin vers le fichier CSV source
        # Charger les données CSV
        with open(f"{DATA_PATH}/output/final.json", 'r') as fp:
            self.data = json.load(fp)

        self.stations = pd.DataFrame.from_dict(self.data["stations"])
        self.hourly = pd.DataFrame.from_dict(self.data["hourly"])

    def test_stations_count_row(self):
        self.assertEqual(self.stations.shape[0], 6, "Nombre de ligne n'est pas égale à 6")

    def test_stations_count_columns(self):
        self.assertEqual(self.stations.shape[1], 10, "Nombre de colonne n'est pas égale à 6")

    def test_stations_doublons(self):
        has_duplicated = bool(self.stations.duplicated(subset=['id', 'name']).any())
        self.assertFalse(has_duplicated, "Station en double")
        
    def test_stations_types(self):
        required_columns = self.stations[['id', 'name', 'latitude', 'longitude', 'elevation', 'type']]
        self.assertTrue(required_columns["id"].dtype == "object", "Type d'id doit être en chaîne de caractère")
        self.assertTrue(required_columns["name"].dtype == "object", "Type de name doit être en chaîne de caractère")
        self.assertTrue(required_columns["latitude"].dtype in ["float64", "int64"], "Type de latitude doit être numérique")
        self.assertTrue(required_columns["longitude"].dtype in ["float64", "int64"], "Type de longitude doit être numérique")
        self.assertTrue(required_columns["elevation"].dtype in ["float64", "int64"], "Type d'elevation doit être numérique")
        self.assertTrue(required_columns["type"].dtype == "object", "Type de type doit être en chaîne de caractère")

    def test_hourly_count_row(self):
        self.assertEqual(self.hourly.shape[0],4950, "Nombre de ligne n'est pas égale à 5175")

    def test_hourly_count_columns(self):
        self.assertEqual(self.hourly.shape[1], 19, "Nombre de colonne n'est pas égale à 19")

    def test_hourly_doublons(self):
        has_duplicated = bool(self.hourly.duplicated(subset=['id_station', 'dh_utc']).any())
        self.assertFalse(has_duplicated, "Horaire de mesure en double")
        
    def test_hourly_types(self):
        required_columns = self.hourly[['id_station', 'dh_utc', 'temperature', 'pression', 'humidite']]
        self.assertTrue(required_columns["dh_utc"].dtype == "object", "Type de dh_utc doit être en chaîne de caractère")
        try:
            required_columns["temperature"].astype(float)
        except ValueError:
            self.assertTrue(False, "Type de temperature doit être numérique")
        try:
            required_columns["pression"].astype(float)
        except ValueError:
            self.assertTrue(False, "Type de pression doit être numérique")
        try:
            required_columns["humidite"].astype(float)
        except ValueError:
            self.assertTrue(False, "Type de humidite doit être numérique")

    def test_hourly_dhutc_datetime_format(self):
        try:
            pd.to_datetime(self.hourly['dh_utc'])
        except ValueError:
            self.assertTrue(False, "Format de dh_utc ne peut pas convertir en datetime")

    def test_hourly_temperature_plage(self):
        # Test plages de température
        self.assertTrue((-50 <= self.hourly['temperature'].astype(float)).all() and 
                       (self.hourly['temperature'].astype(float) <= 50).all())
        
    def test_hourly_humidite_plage(self):
        # Test plages d'humidité
        self.assertTrue((0 <= self.hourly['humidite'].astype(float)).all() and 
                       (self.hourly['humidite'].astype(float) <= 100).all())


if __name__ == '__main__':
    unittest.main()