from pymongo import MongoClient
from datetime import datetime, timedelta

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

db = client['formatx_db']

files_collection = db['files']

cutoff_time = datetime.utcnow() - timedelta(days=3)
files_collection.delete_many({
    "user_id": None,
    "uploaded_at": {"$lt": cutoff_time.isoformat()}
})

def init_db():
    print("Connect to MongoDB (File Service)")