# Transaction de données vers service MongoDB dans AWS ECS

Ce projet permet de transformer des données brutes de stations métérologique et intégrer ces données météo de stations dans une architecture semi-professionnelles dans le cloud AWS.

## Installation 

1. Mettre à jour les fichiers `.env` et `.env.awsecs` à partir des fichiers .sample

2. Transaction de données et démarrer le serveur de Airbyte localement dans docker-compose

    - Airbyte et traitement de données brutes 
    `docker-compose -f docker-compose.airbyte.yaml --env-file .env.airbyte up -d`

3. Dans le nativateur entrer l'adresse `localhost:8000`
    
    - Dans le sources, créer une source en cherchant `File` et mettre `Local filesystem` puis dans l'URI mettre `/local/output/final.json`
    - Dans la destinations créer une destination et configurer le AWS bucket S3 désiré

    - Créer une connection avec la source et destination créer en haut et synchronisation

4. Démarrer la deuxième docker-compose 

    - Mongodb et Script Python pour injection donnéews dans MongoDB
    `docker-compose -f docker-compose.yaml --env-file .env  up -d`

    Ce docker-compose permet:
        1. créer un replica set de MongoDB, il contient 3 instances MongoDB et 1 instance arbitraire.
        2. Initialiser le replicaset et en créant 3 collections avec des schema validator
        3. Test pré-transaction de données du fichier `final.json`
        4. Transaction de données du fichier `final.json` dans le replica set
        5. Test post-transaction de données dans le replicaset du MongoDB
        6. Faire un reporting sur le temps d'accessiblité
        7. Calculer l'erreur sur les données

    Commande pour vérifier la réplication
    `docker-compose exec  mongodb1 mongosh --host localhost:27017 --eval 'rs.status();'`

5. Création d'instance dans AWS ECS / AWS DocumentDB

    Pour AWS ECS:
    1. Création de cluster
    2. Création de définition de task
    3. Run task definition (Configurer Groupe de sécurité)
    
    Pour DocumentDB:
    Créer un cluster et suivre l'étape de la page de plateforme

6. Transaction des données dans le cloud AWS
    1. Via Airbyte
    2. Par `python insert_to_ecs.py`
