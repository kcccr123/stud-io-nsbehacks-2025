from bson.objectid import ObjectId
from flask import jsonify, request
from utils.db import flashcard_collection  # Ensure your `db.py` handles the flashcards collection

"""

{
  "_id": "unique_flashcard_id",
  "question": "What is BFS?",
  "answer": "Breadth-First Search is ...",
  "embedding": [0.12, 0.45, 0.78, ...], 
  "topic": "Graphs",
  "difficulty": "medium"
}


"""

# Get all flashcards
def get_flashcards():
    flashcards = list(flashcard_collection.find({}, {"_id": 0}))
    return jsonify(flashcards)

# Get a single flashcard by ID
def get_flashcard(flashcard_id):
    flashcard = flashcard_collection.find_one({"_id": ObjectId(flashcard_id)})
    if flashcard:
        flashcard['_id'] = str(flashcard['_id'])
        return jsonify(flashcard)
    return jsonify({"error": "Flashcard not found"}), 404

# Add a new flashcard
def add_flashcard():
    data = request.get_json()
    flashcard_collection.insert_one(data)
    return jsonify({"message": "Flashcard added successfully"}), 201

# Update a flashcard by ID
def update_flashcard(flashcard_id):
    data = request.get_json()
    result = flashcard_collection.update_one({"_id": ObjectId(flashcard_id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Flashcard updated successfully"}), 200
    return jsonify({"error": "Flashcard not found"}), 404

# Delete a flashcard by ID
def delete_flashcard(flashcard_id):
    result = flashcard_collection.delete_one({"_id": ObjectId(flashcard_id)})
    if result.deleted_count:
        return jsonify({"message": "Flashcard deleted successfully"}), 200
    return jsonify({"error": "Flashcard not found"}), 404
