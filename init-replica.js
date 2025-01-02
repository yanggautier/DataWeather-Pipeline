// Initialisation du replica set
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb1:27017" },
    { _id: 1, host: "mongodb2:27017" },
    { _id: 2, host: "mongodb3:27017" },
    { _id: 3, host: "arbiter:27017", arbiterOnly: true }
  ]
});

print("Replica Set with arbiter initiated successfully.");

// Attendre que le replica set soit initialisé
sleep(2000);

// Schéma de validation pour la collection stations
db.createCollection("stations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "name", "latitude", "longitude", "elevation", "source"],
      properties: {
        id: { bsonType: "string" },
        name: { bsonType: "string" },
        latitude: { bsonType: "number", minimum: -90, maximum: 90 },
        longitude: { bsonType: "number", minimum: -180, maximum: 180 },
        elevation: { bsonType: "number" },
        type: { bsonType: "string" },
        license: {
          bsonType: "object",
          properties: {
            license: { bsonType: "string" },
            url: { bsonType: "string" },
            source: { bsonType: "string" },
            metadonnees: { bsonType: "string" }
          }
        },
        source: { bsonType: "string" },
        hardware: { bsonType: "string" },
        software: { bsonType: "string" }
      }
    }
  }
});

// Schéma de validation pour la collection metadata
db.createCollection("metadata", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      additionalProperties: {
        bsonType: "string"
      }
    }
  }
});

// Schéma de validation pour la collection hourly
db.createCollection("hourly", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_station", "dh_utc"],
      properties: {
        id_station: { bsonType: "string" },
        dh_utc: { bsonType: "string" },
        temperature: { bsonType: ["number", "string", "null"] },
        pression: { bsonType: ["number", "string", "null"] },
        humidite: { bsonType: ["number", "string", "null"] },
        point_de_rosee: { bsonType: ["number", "string", "null"] },
        visibilite: { bsonType: ["number", "string", "null"] },
        vent_moyen: { bsonType: ["number", "string", "null"] },
        vent_rafales: { bsonType: ["number", "string", "null"] },
        vent_direction: { bsonType: ["number", "string", "null"] },
        pluie_3h: { bsonType: ["number", "string", "null"] },
        pluie_1h: { bsonType: ["number", "string", "null"] },
        neige_au_sol: { bsonType: ["number", "string", "null"] },
        nebulosite: { bsonType: ["string", "null"] },
        temps_omm: { bsonType: ["string", "null"] },
        precip_rate: { bsonType: ["number", "null"] },
        precip_accum: { bsonType: ["number", "null"] },
        solar: { bsonType: ["number", "null"] },
        uv: { bsonType: ["number", "null"] }
      }
    }
  }
});

print("Collections created with validation schemas.");