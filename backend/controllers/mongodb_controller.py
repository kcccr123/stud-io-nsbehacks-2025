# Place this file under the `controller` directory as `mongo_controller.py`

from bson.objectid import ObjectId
from flask import jsonify, request
from utils.db import collection

# Get all items
def get_items():
    items = list(collection.find({}, {"_id": 0}))
    return jsonify(items)

# Get a single item by ID
def get_item(item_id):
    item = collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

# Add a new item
def add_item():
    data = request.get_json()
    collection.insert_one(data)
    return jsonify({"message": "Item added successfully"}), 201

# Update an item by ID
def update_item(item_id):
    data = request.get_json()
    result = collection.update_one({"_id": ObjectId(item_id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Item updated successfully"}), 200
    return jsonify({"error": "Item not found"}), 404

# Delete an item by ID
def delete_item(item_id):
    result = collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count:
        return jsonify({"message": "Item deleted successfully"}), 200
    return jsonify({"error": "Item not found"}), 404
