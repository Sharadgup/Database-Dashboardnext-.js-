from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
import traceback
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for /api/ routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure the MongoDB Atlas connection
MONGO_URI = 'mongodb+srv://shardgupta65:Typer%401345@cluster0.sp87qsr.mongodb.net/chatgpt'

try:
    client = MongoClient(MONGO_URI)
    db = client['chatgpt']
    items_collection = db['items']
    # Test the connection
    client.admin.command('ping')
    app.logger.info("Successfully connected to MongoDB Atlas!")
except Exception as e:
    app.logger.error(f"Error connecting to MongoDB Atlas: {e}")
    exit(1)

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'index.html')

@app.route('/api/create_table', methods=['POST'])
def create_table():
    try:
        dummy_id = items_collection.insert_one({"dummy": True}).inserted_id
        items_collection.delete_one({"_id": dummy_id})
        return jsonify({"message": "Collection created successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error creating table: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/drop_table', methods=['POST'])
def drop_table():
    try:
        items_collection.drop()
        return jsonify({"message": "Collection dropped successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error dropping table: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_database():
    try:
        items_collection.drop()
        dummy_id = items_collection.insert_one({"dummy": True}).inserted_id
        items_collection.delete_one({"_id": dummy_id})
        return jsonify({"message": "Database refreshed successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error refreshing database: {str(e)}")
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
        app.logger.error(f"Error inserting item: {str(e)}")
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
        app.logger.error(f"Error updating item: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_item(id):
    try:
        result = items_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting item: {str(e)}")
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
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        items = list(items_collection.find())
        for item in items:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return jsonify(items), 200
    except Exception as e:
        app.logger.error(f"Error fetching items: {str(e)}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)