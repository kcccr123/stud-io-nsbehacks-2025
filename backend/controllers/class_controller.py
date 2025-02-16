from bson.objectid import ObjectId
from flask import jsonify, request
from utils.db import class_collection  # Collection for classes

# Add a new class
def add_class():
    data = request.get_json()
    if not data.get("className"):
        return jsonify({"error": "className is required"}), 400
    result = class_collection.insert_one(data)
    return jsonify({"message": "Class added successfully", "class_id": str(result.inserted_id)}), 201

# Delete a class by ID
def delete_class(class_id):
    result = class_collection.delete_one({"_id": ObjectId(class_id)})
    if result.deleted_count:
        return jsonify({"message": "Class deleted successfully"}), 200
    return jsonify({"error": "Class not found"}), 404

# Get all classes
def get_all_classes():
    classes = list(class_collection.find({}, {"className": 1}))  # Include only classnames
    for cls in classes:
        cls["_id"] = str(cls["_id"])
    return jsonify(classes), 200

# Get a single class by ID
def get_single_class(class_id):
    cls = class_collection.find_one({"_id": ObjectId(class_id)})
    if cls:
        cls["_id"] = str(cls["_id"])
        return jsonify(cls), 200
    return jsonify({"error": "Class not found"}), 404