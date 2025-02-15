# Place this file under the `controllers` directory as `user_controller.py`

from bson.objectid import ObjectId
from flask import jsonify, request
from utils.db import user_collection  # Update to handle user collection
import hashlib

# Hash password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

"""

{
  "_id": "user_id",
  "name": "John Doe",
  "performance": {
    "Graphs": {"correct": 5, "incorrect": 2},
    "Algorithms": {"correct": 8, "incorrect": 4}
  },
  "q_table": {
    "state1": [0.5, 0.2, 0.7], 
    "state2": [0.1, 0.9, 0.4]
  }
}

"""

# Register a new user
def register_user():
    data = request.get_json()
    data['password'] = hash_password(data['password'])
    user_collection.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201

# Login user
def login_user():
    data = request.get_json()
    user = user_collection.find_one({"email": data['email']})
    if user and user['password'] == hash_password(data['password']):
        return jsonify({"message": "Login successful", "user_id": str(user['_id'])}), 200
    return jsonify({"error": "Invalid email or password"}), 401

# Save reinforcement learning data for user
def save_rl_data(user_id):
    data = request.get_json()
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "performance": data.get("performance"),
            "q_table": data.get("q_table")
        }}
    )
    if result.matched_count:
        return jsonify({"message": "Reinforcement learning data saved successfully"}), 200
    return jsonify({"error": "User not found"}), 404

# Get reinforcement learning data for user
def get_rl_data(user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "performance": 1, "q_table": 1})
    if user:
        return jsonify(user), 200
    return jsonify({"error": "No reinforcement learning data found"}), 404
