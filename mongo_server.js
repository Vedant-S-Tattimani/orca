const { MongoMemoryServer } = require('mongodb-memory-server');

async function run() {
  const mongod = await MongoMemoryServer.create({
    instance: { port: 27017 }
  });
  
  const uri = mongod.getUri();
  console.log("Memory server running on " + uri);
  
  // Keep the process alive
  setInterval(() => {}, 1000);
}

run();
