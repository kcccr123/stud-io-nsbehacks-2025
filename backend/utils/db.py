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

# Create user and flashcard collections if they do not exist
if "users" not in db.list_collection_names():
    db.create_collection("users")
if "flashcards" not in db.list_collection_names():
    db.create_collection("flashcards")
if "performance_data" not in db.list_collection_names():
    db.create_collection("performance_data")

# Access a collection
user_collection = db.get_collection("users")
flashcard_collection = db.get_collection("flashcards")
performance_collection = db.get_collection("performance_data")

# Export db and collection for use in other modules
__all__ = ['db', 'user_collection', 'flashcard_collection', 'performance_collection']
