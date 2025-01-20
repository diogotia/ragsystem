// Switch to the queryDB database
db = db.getSiblingDB('queryDB');

// Create the queries collection
db.createCollection('queries');

// Create text index on the content field
db.queries.createIndex(
    { content: "text" },
    { default_language: "english" }
);

// Create any other necessary collections
db.createCollection('documents'); 