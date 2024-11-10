from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
import traceback

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure the MongoDB database
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dashboard_db']
    items_collection = db['items']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Serve the HTML file
@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'index.html')

@app.route('/api/create_table', methods=['POST'])
def create_table():
    try:
        # In MongoDB, collections are created automatically when you insert data
        # So we'll just insert a dummy document and then remove it
        dummy_id = items_collection.insert_one({"dummy": True}).inserted_id
        items_collection.delete_one({"_id": dummy_id})
        return jsonify({"message": "Collection created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/drop_table', methods=['POST'])
def drop_table():
    try:
        items_collection.drop()
        return jsonify({"message": "Collection dropped successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_database():
    try:
        items_collection.drop()
        dummy_id = items_collection.insert_one({"dummy": True}).inserted_id
        items_collection.delete_one({"_id": dummy_id})
        return jsonify({"message": "Database refreshed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/insert', methods=['POST'])
def insert_item():
    try:
        data = request.json
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({"error": "Invalid data. 'name' and 'description' are required."}), 400
        result = items_collection.insert_one({
            "name": data['name'],
            "description": data['description']
        })
        return jsonify({"message": "Item inserted successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/update/<id>', methods=['PUT'])
def update_item(id):
    try:
        data = request.json
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({"error": "Invalid data. 'name' and 'description' are required."}), 400
        result = items_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": data['name'], "description": data['description']}}
        )
        if result.modified_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_item(id):
    try:
        result = items_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file:
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            return jsonify({"message": "File uploaded successfully", "filename": filename}), 201
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        items = list(items_collection.find())
        for item in items:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)