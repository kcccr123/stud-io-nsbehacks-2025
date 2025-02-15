from pymongo import MongoClient
import os

# Load environment variables if using a .env file
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection string from your Atlas dashboard
MONGO_URI = os.getenv("MONGO_URI")

# Create a client instance
client = MongoClient(MONGO_URI)

# Access a specific database
db = client.get_database("database_name")

# Access a collection
collection = db.get_collection("collection_name")

# Test connection
def test_connection():
    try:
        # Print the first document in the collection
        document = collection.find_one()
        print("Connected to MongoDB:", document)
    except Exception as e:
        print("Error connecting to MongoDB:", e)

if __name__ == "__main__":
    test_connection()
