from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
import io
import os
import json

app = Flask(__name__)
CORS(app)

# Model setup
def load_model():
    # Load your pretrained model
    model = resnet18()
    # Modify the final fully connected layer to match your number of classes
    num_classes = 14  # Update this if your number of classes has changed
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
    try:
        with open('class_names.json', 'r') as f:
            return json.load(f)
    except:
        # Placeholder class names if file doesn't exist
        return [f"Class_{i}" for i in range(14)]

# Class descriptions - hardcoded for simplicity
class_descriptions = {
    0: "الحرم المكي (The Holy Mosque in Mecca) - The holiest mosque in Islam and the primary destination for the Hajj and Umrah pilgrimages. It surrounds the Kaaba, considered the most sacred site in Islam.",
    1: "العلا (AlUla) - A historic city in northwestern Saudi Arabia, known for its stunning natural rock formations, archaeological sites including Hegra (Saudi Arabia's first UNESCO World Heritage site), and annual Winter at Tantora festival.",
    2: "المسجد النبوي (The Prophet's Mosque) - Located in Medina, this is the second holiest site in Islam. It was built by Prophet Muhammad and houses his tomb.",
    3: "جبل أحد (Mount Uhud) - A mountain north of Medina, famous for being the site of the Battle of Uhud fought in 625 CE. It has great historical and religious significance in Islamic history.",
    4: "برج المملكة (Kingdom Tower) - Also known as Kingdom Centre, it's a 99-story skyscraper in Riyadh. With its distinctive inverted parabolic arch topped by a sky bridge, it's one of Saudi Arabia's most recognizable landmarks.",
    5: "المصمك (Masmak Fort) - A clay and mud-brick fort in the old quarter of Riyadh, with distinctive features including high walls and watchtowers. It played a significant role in the history of Saudi Arabia's unification.",
    6: "برج الفيصلية (Al Faisaliyah Tower) - One of the most distinctive skyscrapers in Riyadh, featuring a golden ball near its top that contains a restaurant with panoramic views of the city.",
    7: "وادي حنيفة (Wadi Hanifa) - A valley that runs through the city of Riyadh. It has been transformed into an environmental, recreational and tourist destination with parks, walking paths, and water features.",
    8: "فقيه أكواريوم (Fakieh Aquarium) - Located in Jeddah, it's the first and largest public aquarium in Saudi Arabia, housing a wide variety of marine life and offering educational exhibits.",
    9: "كورنيش جدة (Jeddah Corniche) - A 30 km coastal resort area in Jeddah along the Red Sea. It features recreational areas, pavilions, large-scale sculptures, and the King Fahd Fountain, the tallest water fountain in the world.",
    10: "برج مياه الخبر (Khobar Water Tower) - A distinctive landmark in the city of Khobar in the Eastern Province, known for its unique architectural design.",
    11: "مسجد قباء (Quba Mosque) - Located in the outskirts of Medina, it's the oldest mosque in the world. According to Islamic tradition, it was founded by Prophet Muhammad when he arrived in Medina.",
    12: "مسجد الراجحي (Al-Rajhi Mosque) - One of the largest mosques in Riyadh, known for its beautiful architecture combining traditional Islamic elements with modern design.",
    13: "المتحف الوطني (The National Museum) - Located in Riyadh, it's the largest museum in Saudi Arabia showcasing the history, culture, and civilization of the Arabian Peninsula."
}

# Initialize model and class names on startup
model = load_model()
class_names = load_class_names()

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
    
    try:
        file = request.files['image']
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        # Transform and process image
        img_tensor = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            # Get the predicted class index directly
            _, predicted_idx = torch.max(outputs, 1)
            class_idx = predicted_idx.item()
            
            # Calculate probabilities for the top 5 classes
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            num_to_return = min(5, len(class_names))
            top_probs, top_indices = torch.topk(probs, num_to_return)
            
        # Get class name and description for the predicted class
        class_name = class_names[str(class_idx)] if str(class_idx) in class_names else f"Class_{class_idx}"
        
        # Get description from the hardcoded dictionary
        description = class_descriptions.get(class_idx, f"No detailed description available for {class_name}")
        
        # Prepare additional top predictions
        predictions = []
        for i in range(num_to_return):
            idx = top_indices[i].item()
            predictions.append({
                'classIndex': idx,
                'className': class_names[str(idx)] if str(idx) in class_names else f"Class_{idx}",
                'score': top_probs[i].item(),
                'description': class_descriptions.get(idx, f"No detailed description available for {class_names[str(idx)] if str(idx) in class_names else f'Class_{idx}'}")
            })
        
        return jsonify({
            'success': True,
            'classIndex': class_idx,
            'className': class_name,
            'description': description,
            'predictions': predictions  # Include top predictions for alternative options
        })
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/api/description/<int:class_index>', methods=['GET'])
def get_description(class_index):
    # Get class name from the index
    class_name = class_names[str(class_index)] if str(class_index) in class_names else f"Class_{class_index}"
    
    # Get description from the hardcoded dictionary
    description = class_descriptions.get(class_index, f"No detailed description available for {class_name}")
    
    return jsonify({
        'success': True,
        'description': description
    })

# No need for the admin route to add descriptions anymore

if __name__ == '__main__':
    app.run(debug=True)