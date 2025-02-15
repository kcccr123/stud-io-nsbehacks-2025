# Place this file under the `controllers` directory as `performance_controller.py`

from bson.objectid import ObjectId
from flask import jsonify, request
from utils.db import performance_collection  # New collection for performance data

# Get performance data for a user
def get_performance(user_id):
    data = performance_collection.find_one({"user_id": ObjectId(user_id)})
    if data:
        return jsonify(data), 200
    return jsonify({"error": "No performance data found"}), 404

# Add or update performance data for a user
def add_update_performance(user_id):
    data = request.get_json()
    result = performance_collection.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {
            "performance": data.get("performance"),
            "q_table": data.get("q_table")
        }},
        upsert=True
    )
    if result.matched_count or result.upserted_id:
        return jsonify({"message": "Performance data updated successfully"}), 200
    return jsonify({"error": "Failed to update performance data"}), 400

# Delete performance data for a user
def delete_performance(user_id):
    result = performance_collection.delete_one({"user_id": ObjectId(user_id)})
    if result.deleted_count:
        return jsonify({"message": "Performance data deleted successfully"}), 200
    return jsonify({"error": "No performance data found"}), 404
