from scripts.etl_to_path import *
import os

DATA_FOLDER = os.getenv("LOCAL_ROOT")


# Charger les données
infoclimat_data,  df_ichtegem, df_madeleine = extract(f"{DATA_FOLDER}/input/Data_Source1_011024-071024.json", f"{DATA_FOLDER}/input/Weather+Underground+-+Ichtegem,+BE.xlsx", f"{DATA_FOLDER}/input/Weather+Underground+-+La+Madeleine,+FR.xlsx")

# Traitement de données
data = transform(infoclimat_data,  df_ichtegem, df_madeleine)

# Sauvegarde de données traitées
load(data, f"{DATA_FOLDER}/output/final.json")