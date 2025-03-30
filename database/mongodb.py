from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

# Create FormatX database
db = client["formatx_db"]

# Collections
users_collection = db["users"]
files_collection = db["files"]
tasks_collection = db["tasks"]

print("Connected to MongoDB!")