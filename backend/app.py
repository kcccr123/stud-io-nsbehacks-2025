from flask import Flask
from controllers.mongodb_controller import get_items, get_item, add_item, update_item, delete_item  # Import all routes
from utils.db import db, collection  # Connect to the database

app = Flask(__name__)

# Test database connection
try:
    db.command('ping')
    print("Successfully connected to the database")
except Exception as e:
    print("Failed to connect to the database:", e)

# Register all routes from mongo_controller
app.add_url_rule('/items', 'get_items', get_items, methods=['GET'])
app.add_url_rule('/items/<item_id>', 'get_item', get_item, methods=['GET'])
app.add_url_rule('/items', 'add_item', add_item, methods=['POST'])
app.add_url_rule('/items/<item_id>', 'update_item', update_item, methods=['PUT'])
app.add_url_rule('/items/<item_id>', 'delete_item', delete_item, methods=['DELETE'])

if __name__ == "__main__":
    app.run(debug=True)
