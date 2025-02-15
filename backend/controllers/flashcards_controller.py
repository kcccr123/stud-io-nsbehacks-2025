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


# def add_flashcard():
#     data = request.get_json()
#     question = data.get("question")
#     answer = data.get("answer")

#     # Generate embedding using OpenAI API
#     response = client.embeddings.create(input=f"{question} {answer}", model="text-embedding-ada-002")
#     embedding = response.data[0].embedding

#     flashcard_data = {
#         "question": question,
#         "answer": answer,
#         "embedding": embedding,
#         "topic": data.get("topic"),
#         "difficulty": data.get("difficulty")
#     }
#     flashcard_collection.insert_one(flashcard_data)
#     return jsonify({"message": "Flashcard added successfully with embedding"}), 201

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

# Search flashcards by vector similarity
def search_flashcards_by_vector():
    data = request.get_json()
    query_embedding = data.get("embedding")
    top_k = data.get("top_k", 5)

    results = flashcard_collection.aggregate([
        {
            "$vectorSearch": {
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": top_k,
                "index": "flashcard_vector_index"
            }
        }
    ])
    return jsonify(list(results))
