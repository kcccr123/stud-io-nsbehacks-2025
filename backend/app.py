from flask import Flask, jsonify, request
from db import db, collection

app = Flask(__name__)

@app.route('/items', methods=['GET'])
def get_items():
    items = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB object ID
    return jsonify(items)

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    collection.insert_one(data)
    return jsonify({"message": "Item added successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)
