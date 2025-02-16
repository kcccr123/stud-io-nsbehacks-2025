from bson.objectid import ObjectId
from flask import jsonify, request
from sentence_transformers import SentenceTransformer
from pymongo.operations import SearchIndexModel
from bson.binary import Binary, BinaryVectorDtype
from utils.db import flashcard_collection
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

# Embedding generation functions
def get_embedding(data, precision="float32"):
    return model.encode(data, precision=precision)

def generate_bson_vector(vector, vector_dtype):
    return Binary.from_vector(vector, vector_dtype)

# Updated add_flashcard method using BSON-based embeddings
def add_flashcard():
    data = request.get_json()
    text = f"{data.get('question')} {data.get('answer')}"

    # Generate embeddings
    float32_embedding = get_embedding(text, "float32")
    bson_float32_embedding = generate_bson_vector(float32_embedding, BinaryVectorDtype.FLOAT32)

    flashcard_data = {
        "question": data.get("question"),
        "answer": data.get("answer"),
        "embedding": bson_float32_embedding,
        "topic": data.get("topic"),
        "difficulty": data.get("difficulty")
    }

    flashcard_collection.insert_one(flashcard_data)
    return jsonify({"message": "Flashcard added with BSON vector embedding"}), 201

# Define the find_similar_flashcards API call using vector search
def find_similar_flashcards():
    data = request.get_json()
    query_text = data.get("query")
    top_k = data.get("top_k", 5)

    # Generate embedding for the query
    query_embedding = get_embedding(query_text, "float32")

    # Run the vector search query
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "limit": top_k,
                "numCandidates": 100
            }
        },
        {
            "$project": {
                "question": 1,
                "answer": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(flashcard_collection.aggregate(pipeline))
    return jsonify(results), 200

def add_flashcard_func(flashcard_data):
    """
    Refactored: Now a regular function that accepts a Python dictionary.
    
    flashcard_data should be a dict with keys:
      - "question" (str)
      - "answer" (str)
      - "topic" (optional, str)
      - "difficulty" (optional, str)

    Returns:
      A tuple: (response_json, status_code)
        Where response_json is a Python dictionary, typically passed to jsonify() by the caller.
        status_code is an HTTP-like status code (e.g., 201).
    """
    # 1. Build text to embed (e.g., "Question Answer")
    text = f"{flashcard_data.get('question', '')} {flashcard_data.get('answer', '')}"

    # 2. Generate embedding
    float32_embedding = get_embedding(text, "float32")
    bson_float32_embedding = generate_bson_vector(float32_embedding, BinaryVectorDtype.FLOAT32)

    # 3. Build document for MongoDB
    doc = {
        "question": flashcard_data.get("question"),
        "answer": flashcard_data.get("answer"),
        "embedding": bson_float32_embedding,
        "topic": flashcard_data.get("topic"),
        "difficulty": flashcard_data.get("difficulty")
    }

    # 4. Insert into the collection
    result = flashcard_collection.insert_one(doc)

    # 5. Return a response-like dict plus an HTTP-like status
    return (
        {
            "message": "Flashcard added with BSON vector embedding",
            "flashcard_id": str(result.inserted_id)
        },
        201
    )

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

# Define the find_similar_flashcards API call using vector search
def find_similar_flashcards():
    data = request.get_json()
    query_text = data.get("query")
    top_k = data.get("top_k", 5)

    # Generate embedding for the query
    query_embedding = get_embedding(query_text, "float32").tolist()  # Convert to list for MongoDB

    # Run the vector search query
    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "flashcard_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "limit": top_k,
                    "numCandidates": 100,
                    "numDimensions": 768  # Match the indexed dimension size

                }
            },
            {
                "$project": {
                    "_id": 0,  # Exclude ObjectId from the output
                    "question": 1,
                    "answer": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = list(flashcard_collection.aggregate(pipeline))
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400