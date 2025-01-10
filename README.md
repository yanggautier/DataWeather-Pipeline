# Transaction de données vers service MongoDB dans AWS ECS

Ce projet permet de transformer des données brutes de stations météorologiques et intégrer ces données météo dans une architecture semi-professionnelle dans le cloud AWS.

## Table des matières

- [Installation](#installation)
  - [Prérequis](#prérequis)
  - [Configuration Airbyte](#configuration-airbyte)
  - [Configuration MongoDB](#configuration-mongodb)
  - [Déploiement AWS](#déploiement-aws)
- [Architecture](#architecture)
- [Configuration Docker](#configuration-docker)

## Installation

### Prérequis
1. Mettre à jour les fichiers `.env` et `.env.awsecs` à partir des fichiers `.sample`

### Configuration Airbyte

1. Démarrer Airbyte et le traitement des données :
```bash
docker-compose -f docker-compose.airbyte.yaml --env-file .env.airbyte up -d
```

2. Configurer l'interface Airbyte (localhost:8000) :
   - Dans Sources : sélectionner "File" > "Local filesystem"
   - URI source : `/local/output/final.json`
   - Dans Destinations : configurer le bucket AWS S3
   - Créer une connexion source-destination et lancer la synchronisation

### Configuration MongoDB

1. Démarrer l'environnement MongoDB :
```bash
docker-compose up -d
```

Ce déploiement :
- Configure un replica set MongoDB (3 instances + 1 arbitre)
- Initialise les collections avec schémas
- Exécute les tests pré/post-transaction
- Génère les rapports d'accessibilité et d'erreurs

Vérifier la réplication :
```bash
docker-compose exec mongodb1 mongosh --host localhost:27017 --eval 'rs.status();'
```

### Déploiement AWS

#### ECS
1. Créer un cluster
2. Définir une tâche
3. Exécuter la tâche (configurer le groupe de sécurité)

#### DocumentDB
- Suivre la documentation AWS pour la création du cluster

#### Migration des données
```bash
# Via Python
python insert_to_ecs.py

# Ou via Airbyte
# Utiliser l'interface web configurée précédemment
```

## Architecture

```
project/
├── notebooks
│   └── Connect_ECS.ipynb
│   └── Transform_data.ipynb
├── Dockerfile
├── Dockerfile.aribyte_src_python
├── README.md
├── data
│   ├── input
│   │   ├── Data_Source1_011024-071024.json
│   │   ├── Weather+Underground+-+Ichtegem,+BE.xlsx
│   │   └── Weather+Underground+-+La+Madeleine,+FR.xlsx
│   └── output
│       └── final.json
├── dico_données.xlsx
├── docker-compose.airbyte.yaml
├── docker-compose.yml
├── flags.yml
├── ingest_mongodb.py
├── init-replica.js
├── insert_to_ecs.py
├── requirements.txt
├── scripts
│   ├── etl_to_mongodb.py
│   ├── etl_to_path.py
│   ├── reporting_time.py
│   └── schema_validator.py
├── tests
│   ├── post_test_migration.py
│   └── pre_test_migration.py
├── .env
├── .env.awsecs
├── .env.airbyte
├── requirements.txt
└── to_json.py
```

## Configuration Docker

Le projet utilise deux fichiers docker-compose :

### docker-compose.airbyte.yaml
Gère la configuration Airbyte et contient les services suivants :
- init
- bootloader
- db
- worker
- server
- webapp
- airbyte-temporal
- airbyte-cron
- airbyte-connector-builder-server
- airbyte-proxy
- python_etl

### docker-compose.yml
Configure l'environnement MongoDB avec :
- mongodb1, mongodb2, mongodb3 (replica set)
- arbiter
- init-replica
- python_processor


## Licence

[MIT](LICENSE)
