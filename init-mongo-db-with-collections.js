const dbName = "tradata";
const collectionName = "btc-prices";
const collectionNameTwo = "tradesignal";

db = db.getSiblingDB(dbName);
db.createCollection(collectionName);
db.createCollection(collectionNameTwo);
db[collectionName].createIndex({ opendate: 1 }, { unique: true });
db[collectionName].createIndex({ closedate: 1 }, { unique: true });

print(`Created DB '${dbName}', collection '${collectionName}', with unique index on 'opendate' and 'closedate'.`);