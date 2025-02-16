# Place this file under the `controllers` directory as `performance_controller.py`

from bson.objectid import ObjectId, InvalidId
from flask import jsonify, request
from utils.db import performance_collection  # New collection for performance data
from utils.db import flashcard_collection, performance_collection
import numpy as np
from collections import defaultdict
ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor


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

# Retrieve Q-table for a user
def get_q_table(user_id):
    user_data = performance_collection.find_one({"user_id": ObjectId(user_id)})
    if user_data and "q_table" in user_data:
        return defaultdict(lambda: defaultdict(float), user_data["q_table"])
    return defaultdict(lambda: defaultdict(float))

# Save Q-table for a user
def save_q_table(user_id, q_table):
    performance_collection.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"q_table": dict(q_table)}},
        upsert=True
    )

# Update Q-values based on user performance
def update_q_table(user_id, flashcard_id, action, reward):
    q_table = get_q_table(user_id)
    if flashcard_id not in q_table:
        q_table[flashcard_id] = {"correct": 0.0, "incorrect": 0.0}
    
    old_value = q_table[flashcard_id][action]
    next_max = max(q_table[flashcard_id].values(), default=0)
    q_table[flashcard_id][action] = old_value + ALPHA * (reward + GAMMA * next_max - old_value)
    save_q_table(user_id, q_table)

# Recommend questions using Q-learning
def recommend_questions(user_id):
    q_table = get_q_table(user_id)
    sorted_questions = sorted(q_table.items(), key=lambda x: min(x[1].values()))
    print(sorted_questions)
    return [item[0] for item in sorted_questions[:5]]

def get_recommended_flashcards(user_id):
    try:
        recommended_ids = recommend_questions(user_id)
        valid_ids = []
        for i in recommended_ids:
            try:
                valid_ids.append(ObjectId(i))
            except InvalidId:
                print(f"Invalid ObjectId skipped: {i}")

        results = list(flashcard_collection.find({"_id": {"$in": valid_ids}}, {"_id": 1, "question": 1, "answer": 1}))

        # Convert ObjectId to string
        for result in results:
            result['_id'] = str(result['_id'])

        return results  # Return data directly, not jsonify
    except Exception as e:
        return {"error": str(e)}

# Log user performance and update Q-table
def log_user_performance(user_id):
    data = request.get_json()
    flashcard_id = data.get("flashcard_id")
    action = data.get("action")
    reward = data.get("reward", 0)
    update_q_table(user_id, flashcard_id, action, reward)
    return jsonify({"message": "Performance logged successfully"}), 200