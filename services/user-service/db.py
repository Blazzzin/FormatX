from pymongo import MongoClient

# MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

# Connect to the `formatx_db` database
db = client["formatx_db"]

# Collections
users_collection = db["users"]

def init_db():
    print("Connected to MongoDB (User Service)")