import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri_here")
client = MongoClient(MONGO_URI)
db = client["lead_db"]
leads_collection = db["leads"]
