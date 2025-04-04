from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Add this import
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
import io
import os
import sqlite3
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Model setup
def load_model():
    # Load your pretrained model
    model = resnet18()
    # Modify the final fully connected layer to match your number of classes
    num_classes = 14  # Replace with your actual number of classes
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    
    # Load your saved weights
    model.load_state_dict(torch.load('model_weights.pth', map_location=torch.device('cpu')))
    model.eval()
    return model

# Image transformation
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load class names
def load_class_names():
    # Replace this with your actual class names
    try:
        with open('class_names.json', 'r') as f:
            return json.load(f)
    except:
        # Placeholder class names if file doesn't exist
        return [f"Class_{i}" for i in range(10)]

# Database setup
def get_db_connection():
    conn = sqlite3.connect('class_descriptions.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS class_descriptions (
        class_index INTEGER PRIMARY KEY,
        class_name TEXT NOT NULL,
        description TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize database and model on startup
model = load_model()
class_names = load_class_names()
init_db()

# Routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.js')
def serve_js():
    return send_from_directory(app.static_folder, 'app.js')

@app.route('/api/classify', methods=['POST'])
def classify_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    
    # Transform and process image
    img_tensor = transform(img).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)[0]
        
    # Get top 5 predictions (or fewer if there are fewer classes)
    num_to_return = min(5, len(class_names))
    top_probs, top_indices = torch.topk(probs, num_to_return)
    
    # Prepare results
    predictions = []
    for i in range(num_to_return):
        class_idx = top_indices[i].item()
        predictions.append({
            'classIndex': class_idx,
            'className': class_names[class_idx] if class_idx < len(class_names) else f"Class_{class_idx}",
            'score': top_probs[i].item()
        })
    
    return jsonify({
        'success': True,
        'predictions': predictions
    })

@app.route('/api/description/<int:class_index>', methods=['GET'])
def get_description(class_index):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM class_descriptions WHERE class_index = ?", (class_index,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'success': True,
            'description': result['description']
        })
    else:
        # If description not found, return a placeholder
        return jsonify({
            'success': False,
            'description': f"No detailed description available for {class_names[class_index] if class_index < len(class_names) else f'Class_{class_index}'}"
        })

# For demonstration, add a route to populate the database
@app.route('/api/admin/add_description', methods=['POST'])
def add_description():
    data = request.json
    if not data or 'class_index' not in data or 'description' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get class name from the index
    class_name = class_names[data['class_index']] if data['class_index'] < len(class_names) else f"Class_{data['class_index']}"
    
    # Insert or update description
    cursor.execute("""
    INSERT OR REPLACE INTO class_descriptions (class_index, class_name, description) 
    VALUES (?, ?, ?)
    """, (data['class_index'], class_name, data['description']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)