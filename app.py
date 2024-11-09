from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/api/create_table', methods=['POST'])
def create_table():
    try:
        with app.app_context():
            db.create_all()
        return jsonify({"message": "Table created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drop_table', methods=['POST'])
def drop_table():
    try:
        with app.app_context():
            db.drop_all()
        return jsonify({"message": "Table dropped successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_database():
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
        return jsonify({"message": "Database refreshed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/insert', methods=['POST'])
def insert_item():
    data = request.json
    new_item = Item(name=data['name'], description=data['description'])
    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Item inserted successfully", "id": new_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/update/<int:id>', methods=['PUT'])
def update_item(id):
    item = Item.query.get_or_404(id)
    data = request.json
    try:
        item.name = data['name']
        item.description = data['description']
        db.session.commit()
        return jsonify({"message": "Item updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = Item.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 201

if __name__ == '__main__':
    app.run(debug=True)